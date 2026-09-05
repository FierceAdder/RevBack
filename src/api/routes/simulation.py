"""Simulation & Benchmark Comparison Endpoints.

Allows merchants to test synthetic collections, run head-to-head ERP baseline benchmarks,
and seed the database for live dashboard demonstration.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, Field

from src.db.session import get_db
from src.models.db_models import (
    Customer, Invoice, InvoiceStatus, RecoveryStage, RelationshipTier,
    ToneType, Promise, PromiseStatus, Communication, CommunicationChannel,
    CommunicationDirection, AuditLog, HumanApproval, PaymentPlan, PaymentPlanInstallment,
    ApprovalStatus, ApprovalType
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
    invoice_count: int = Field(default=25, ge=5, le=100)
    include_disputes: bool = Field(default=True)
    random_seed: int = Field(default=42)


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
        seed=payload.random_seed,
    )

    report = await RecoveryEvaluator.evaluate_batch(
        invoices=invoices,
        include_baseline=True,
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

    try:
        if payload.clear_existing:
            await db.execute(delete(HumanApproval))
            await db.execute(delete(PaymentPlanInstallment))
            await db.execute(delete(PaymentPlan))
            await db.execute(delete(AuditLog))
            await db.execute(delete(Communication))
            await db.execute(delete(Promise))
            await db.execute(delete(Invoice))
            await db.execute(delete(Customer))
            await db.commit()

        # Query any existing invoice numbers to prevent duplicate key errors
        existing_invoices_res = await db.execute(select(Invoice.invoice_number))
        existing_invoice_numbers = set(existing_invoices_res.scalars().all())

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
                existing_cust = (await db.execute(select(Customer).where(Customer.name == cust_name))).scalar_one_or_none()
                if existing_cust:
                    created_customers[cust_name] = existing_cust
                else:
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

            # Guarantee unique invoice_number
            inv_number = item["invoice_number"]
            counter = 1
            while inv_number in existing_invoice_numbers:
                inv_number = f"INV-2026-{now.strftime('%H%M%S')}-{counter:03d}"
                counter += 1
            existing_invoice_numbers.add(inv_number)

            due_date = now - timedelta(days=item["days_overdue"])
            invoice = Invoice(
                customer_id=customer.id,
                invoice_number=inv_number,
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

            # Seed human approval queue items for chronic delayers or ghost defaulters
            if archetype_val in ("GHOST_DEFAULTER", "CHRONIC_DELAYER") and (invoices_created % 5 == 0):
                approval_type = ApprovalType.LEGAL_NOTICE if archetype_val == "GHOST_DEFAULTER" else ApprovalType.CONFIDENCE_ESCALATION
                reason = "Chronic non-responsiveness (>60 days overdue). Formal legal demand notice required." if approval_type == ApprovalType.LEGAL_NOTICE else "Debtor requested unapproved 60-day debt standstill; confidence gate triggered."
                draft = (
                    f"FORMAL NOTICE OF DEMAND UNDER SECTION 138 / COMMERCIAL DISPUTE ACT\n"
                    f"To: {customer.name}\n"
                    f"Ref Invoice: #{invoice.invoice_number} for ₹{invoice.amount_paise / 100:,.2f}\n\n"
                    f"Take notice that an outstanding balance of ₹{invoice.amount_paise / 100:,.2f} remains unpaid despite multiple reminders. "
                    f"You are hereby given 7 business days to remit payment via the attached secure Razorpay link:\n"
                    f"https://rzp.io/i/demo_{invoice.id[:8]}\n\n"
                    f"Failure to remit will result in formal civil recovery proceedings without further communication."
                )
                approval = HumanApproval(
                    invoice_id=invoice.id,
                    action_type=approval_type,
                    proposed_action_details={
                        "level": 6 if approval_type == ApprovalType.LEGAL_NOTICE else 4,
                        "reason": reason,
                        "message_draft": draft,
                        "channel": "FORMAL_NOTICE" if approval_type == ApprovalType.LEGAL_NOTICE else "EMAIL",
                    },
                    confidence=0.62 if approval_type == ApprovalType.CONFIDENCE_ESCALATION else 0.94,
                    threshold=0.85,
                    status=ApprovalStatus.PENDING,
                )
                db.add(approval)

        await db.commit()

        return SeedDatabaseResponse(
            message="Database successfully seeded with realistic B2B receivables",
            customers_created=len(created_customers),
            invoices_created=invoices_created,
            total_invoiced_inr=total_invoiced_paise / 100.0,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database seeding error: {str(e)}")
