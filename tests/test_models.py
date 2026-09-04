"""Tests for database models, relationships, bitemporal fields, and Pydantic schemas."""

from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy import select

from src.models.db_models import (
    Customer, Invoice, Promise, PaymentPlan, PaymentPlanInstallment,
    Communication, AuditLog, HumanApproval,
    InvoiceStatus, RecoveryStage, RelationshipTier, CommunicationChannel,
    ToneType, PromiseStatus, PlanStatus, ApprovalType, ApprovalStatus
)
from src.models.schemas import (
    CustomerCreate, CustomerRead, InvoiceRead, GateResult, RecoveryPrediction
)


@pytest.mark.asyncio
async def test_create_customer_and_invoice(db_session):
    """Verify customer and invoice insertion with relationships."""
    customer = Customer(
        name="Acme Corp India",
        email="finance@acme.in",
        phone="+919876543210",
        relationship_tier=RelationshipTier.KEY_ACCOUNT,
        credit_score=750,
        total_invoiced_paise=500_000_00,
        historical_recovery_rate=0.92,
    )
    db_session.add(customer)
    await db_session.flush()

    assert customer.id is not None

    due = datetime.now(timezone.utc) - timedelta(days=15)
    invoice = Invoice(
        customer_id=customer.id,
        invoice_number="INV-2026-001",
        amount_paise=250_000_00,  # ₹2,50,000
        due_date=due,
        status=InvoiceStatus.PENDING,
        current_stage=RecoveryStage.INTAKE,
        current_level=1,
        risk_score=35.5,
        recovery_probability=0.78,
    )
    db_session.add(invoice)
    await db_session.commit()

    # Query back
    stmt = select(Invoice).where(Invoice.invoice_number == "INV-2026-001")
    result = await db_session.execute(stmt)
    fetched_invoice = result.scalar_one()

    assert fetched_invoice.id is not None
    assert fetched_invoice.amount_paise == 250_000_00
    assert fetched_invoice.customer_id == customer.id
    assert fetched_invoice.valid_at is not None
    assert fetched_invoice.recorded_at is not None


@pytest.mark.asyncio
async def test_bitemporal_promise_and_timeline(db_session):
    """Verify bitemporal timestamps on promises and audit logging."""
    customer = Customer(
        name="Nova Logistics",
        email="accounts@novalog.in",
    )
    db_session.add(customer)
    await db_session.flush()

    invoice = Invoice(
        customer_id=customer.id,
        invoice_number="INV-2026-002",
        amount_paise=100_000_00,
        due_date=datetime.now(timezone.utc) - timedelta(days=20),
    )
    db_session.add(invoice)
    await db_session.flush()

    valid_time = datetime.now(timezone.utc) + timedelta(days=5)
    promise = Promise(
        invoice_id=invoice.id,
        promised_amount_paise=100_000_00,
        promise_date=valid_time,
        status=PromiseStatus.ACTIVE,
        confidence=0.92,
        raw_quote="We will transfer the full payment of ₹1,00,000 by this Friday.",
        valid_at=valid_time,
    )
    db_session.add(promise)

    audit = AuditLog(
        invoice_id=invoice.id,
        event_type="PROMISE_RECORDED",
        actor="AGENT",
        action="Extracted promise to pay from debtor email",
        previous_state="INTAKE",
        new_state="PROMISE_TRACKING",
        reasoning="Debtor provided explicit date and amount commitment",
        confidence_score=0.92,
        token_cost_usd=0.00045,
    )
    db_session.add(audit)
    await db_session.commit()

    # Verify relationships
    stmt = select(Promise).where(Promise.invoice_id == invoice.id)
    res = await db_session.execute(stmt)
    fetched_promise = res.scalar_one()
    assert fetched_promise.status == PromiseStatus.ACTIVE
    assert fetched_promise.confidence == 0.92
    assert fetched_promise.valid_at == valid_time
    assert fetched_promise.recorded_at is not None


@pytest.mark.asyncio
async def test_payment_plan_with_installments(db_session):
    """Verify dynamic payment plan creation with nested installments."""
    customer = Customer(name="Zenith Retail", email="pay@zenith.in")
    db_session.add(customer)
    await db_session.flush()

    invoice = Invoice(
        customer_id=customer.id,
        invoice_number="INV-2026-003",
        amount_paise=300_000_00,  # ₹3,00,000
        due_date=datetime.now(timezone.utc) - timedelta(days=30),
    )
    db_session.add(invoice)
    await db_session.flush()

    plan = PaymentPlan(
        invoice_id=invoice.id,
        total_amount_paise=300_000_00,
        installment_count=3,
        frequency_days=14,
        status=PlanStatus.ACTIVE,
        terms_summary="3 bi-weekly installments of ₹1,00,000 each",
    )
    db_session.add(plan)
    await db_session.flush()

    for i in range(1, 4):
        inst = PaymentPlanInstallment(
            payment_plan_id=plan.id,
            installment_number=i,
            amount_paise=100_000_00,
            due_date=datetime.now(timezone.utc) + timedelta(days=14 * i),
            status="PENDING" if i > 1 else "PAID",
        )
        db_session.add(inst)

    await db_session.commit()

    stmt = select(PaymentPlanInstallment).where(PaymentPlanInstallment.payment_plan_id == plan.id)
    installments = (await db_session.execute(stmt)).scalars().all()
    assert len(installments) == 3
    assert sum(inst.amount_paise for inst in installments) == 300_000_00


def test_pydantic_schemas():
    """Verify Pydantic schemas serialization and validations."""
    gate = GateResult(
        passed=True,
        action="proceed",
        task="promise_extraction",
        confidence=0.88,
        threshold=0.85,
        invoice_amount=250_000_00,
    )
    assert gate.passed is True
    assert gate.action == "proceed"

    pred = RecoveryPrediction(
        recovery_probability=0.74,
        risk_band="MEDIUM",
        recommended_path="GENTLE_WHATSAPP_PAYMENT_LINK",
        factors={"overdue_days": 12.0, "credit_score": 720.0},
        suggested_level=2,
        suggested_tone=ToneType.COLLABORATIVE,
    )
    assert pred.recovery_probability == 0.74
    assert pred.risk_band == "MEDIUM"
