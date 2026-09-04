"""Simulation & Benchmark Comparison Endpoints.

Allows merchants to test synthetic collections, run head-to-head ERP baseline benchmarks,
and seed the database for live dashboard demonstration.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, Field

from src.db.session import get_db
from src.models.db_models import (
    Customer, Invoice, InvoiceStatus, RecoveryStage, RelationshipTier,
    ToneType, Promise, PromiseStatus, Communication, CommunicationChannel,
    CommunicationDirection, AuditLog
)
from src.simulation.generator import DatasetGenerator
from src.evaluation.evaluator import RecoveryEvaluator


router = APIRouter(prefix="/simulation", tags=["Simulation & Benchmarks"])


class SeedDatabaseRequest(BaseModel):
    count: int = Field(default=25, ge=5, le=100, description="Number of synthetic invoices to generate")
    clear_existing: bool = Field(default=False, description="Whether to purge existing data first")
    seed: int = Field(default=42, description="Random seed for reproducibility")


class SeedDatabaseResponse(BaseModel):
    message: str
    customers_created: int
    invoices_created: int
    total_invoiced_inr: float


class SimulationRunPayload(BaseModel):
    invoice_count: int = Field(default=20, ge=5, le=100)
    seed: int = Field(default=42)
    include_baseline: bool = True


@router.post("/run", response_model=Dict[str, Any])
async def run_comparative_simulation(
    payload: SimulationRunPayload,
):
    """
    Executes a head-to-head empirical simulation comparing the autonomous RevBack AI Agent
    against the static ERP dunning baseline across identical receivables.
    Returns recovery rate uplift, DSO reduction, and token spend ROI.
    """
    invoices = DatasetGenerator.generate_invoices(
        count=payload.invoice_count,
        seed=payload.seed,
    )

    report = await RecoveryEvaluator.evaluate_batch(
        invoices=invoices,
        include_baseline=payload.include_baseline,
    )
    return report


@router.post("/seed", response_model=SeedDatabaseResponse, status_code=status.HTTP_201_CREATED)
async def seed_demo_database(
    payload: SeedDatabaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Seeds the active database with realistic Indian B2B companies, overdue invoices,
    and bitemporal commitments across all 5 debtor archetypes for instant dashboard demonstration.
    """
    now = datetime.now(timezone.utc)

    if payload.clear_existing:
        await db.execute(delete(AuditLog))
        await db.execute(delete(Communication))
        await db.execute(delete(Promise))
        await db.execute(delete(Invoice))
        await db.execute(delete(Customer))
        await db.commit()

    synthetic_invoices = DatasetGenerator.generate_invoices(
        count=payload.count,
        seed=payload.seed,
        reference_date=now,
    )

    created_customers = {}
    invoices_created = 0
    total_invoiced_paise = 0

    for item in synthetic_invoices:
        cust_name = item["customer_name"]
        tier = RelationshipTier(item.get("relationship_tier", "STANDARD"))

        if cust_name not in created_customers:
            cust = Customer(
                name=cust_name,
                email=item["customer_email"],
                phone=item.get("customer_phone", "+919876543210"),
                business_type=item.get("business_type", "B2B_SAAS"),
                relationship_tier=tier,
                credit_score=item.get("credit_score", 720),
                total_invoiced_paise=0,
                total_recovered_paise=0,
                historical_recovery_rate=item.get("historical_recovery_rate", 0.85),
            )
            db.add(cust)
            await db.flush()
            created_customers[cust_name] = cust

        customer = created_customers[cust_name]

        due_date = now - timedelta(days=item["days_overdue"])
        invoice = Invoice(
            customer_id=customer.id,
            invoice_number=item["invoice_number"],
            amount_paise=item["amount_paise"],
            amount_paid_paise=0,
            due_date=due_date,
            status=InvoiceStatus.DISPUTED if item.get("is_disputed") else InvoiceStatus.PENDING,
            current_stage=RecoveryStage.INTAKE,
            current_level=1,
            risk_score=float(item.get("days_overdue", 10) * 1.2),
            recovery_probability=0.75,
            dispute_reason="Billing quantity mismatch disputed by client" if item.get("is_disputed") else None,
            valid_at=now,
            recorded_at=now,
        )
        db.add(invoice)
        await db.flush()

        customer.total_invoiced_paise += item["amount_paise"]
        total_invoiced_paise += item["amount_paise"]
        invoices_created += 1

        archetype_val = item.get("archetype", item.get("debtor_archetype", "STANDARD"))
        # Seed initial audit log
        audit = AuditLog(
            invoice_id=invoice.id,
            event_type="INVOICE_INGESTED",
            actor="SYSTEM",
            action=f"Seeded invoice #{invoice.invoice_number} ({archetype_val})",
            previous_state=None,
            new_state=invoice.status.value,
            recorded_at=now,
        )
        db.add(audit)

        # Seed a broken promise for chronic delayers to demonstrate progressive escalation
        if archetype_val == "CHRONIC_DELAYER":
            broken_p = Promise(
                invoice_id=invoice.id,
                promised_amount_paise=invoice.amount_paise,
                promise_date=due_date + timedelta(days=5),
                status=PromiseStatus.BROKEN,
                confidence=0.92,
                raw_quote="We will definitely clear this by Monday.",
                valid_at=due_date + timedelta(days=2),
                recorded_at=due_date + timedelta(days=2),
            )
            db.add(broken_p)

    await db.commit()

    return SeedDatabaseResponse(
        message="Database successfully seeded with realistic B2B receivables",
        customers_created=len(created_customers),
        invoices_created=invoices_created,
        total_invoiced_inr=total_invoiced_paise / 100.0,
    )
