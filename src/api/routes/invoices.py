"""Invoice Management & Recovery Agent Execution Endpoints.

Handles invoice lifecycle, debtor reply ingestion, LangGraph recovery agent triggers,
and tamper-evident legal evidence bundling.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from src.db.session import get_db
from src.models.db_models import (
    Invoice, Customer, Promise, PaymentPlan, PaymentPlanInstallment,
    Communication, AuditLog, HumanApproval, InvoiceStatus, RecoveryStage,
    RelationshipTier, ToneType, PromiseStatus, ApprovalType, ApprovalStatus,
    CommunicationChannel, CommunicationDirection
)
from src.models.schemas import (
    InvoiceRead, InvoiceDetailRead, InvoiceCreate
)
from src.agent.graph import recovery_agent
from src.agent.tools import EvidenceBundler
from src.llm.extractors import DebtorExtractors
from pydantic import BaseModel, Field


router = APIRouter(prefix="/invoices", tags=["Invoices"])


# ---------------- Additional Request/Response Schemas ---------------- #

class InboundMessageRequest(BaseModel):
    message: str = Field(..., description="Message text sent by debtor")
    channel: str = Field(default="EMAIL", description="WHATSAPP, EMAIL, SMS")
    sender: Optional[str] = None


class InboundMessageResponse(BaseModel):
    invoice_id: str
    intent: str
    intent_confidence: float
    is_disputed: bool
    dispute_category: Optional[str] = None
    has_promise: bool
    promised_amount_paise: Optional[int] = None
    promise_date: Optional[str] = None
    promise_confidence: Optional[float] = None
    agent_action_taken: str


class ProcessInvoiceResponse(BaseModel):
    invoice_id: str
    invoice_number: str
    current_stage: str
    current_level: int
    risk_score: float
    recovery_probability: float
    selected_channel: str
    selected_tone: str
    payment_link_url: Optional[str] = None
    requires_human_approval: bool
    approval_reason: Optional[str] = None
    dispatched_message: Optional[str] = None


# ---------------- Endpoints ---------------- #

@router.get("", response_model=List[InvoiceRead])
async def list_invoices(
    stage: Optional[RecoveryStage] = None,
    status: Optional[InvoiceStatus] = None,
    relationship_tier: Optional[RelationshipTier] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Lists invoices with stage, status, and relationship tier filters."""
    query = select(Invoice).options(selectinload(Invoice.customer))

    if stage:
        query = query.where(Invoice.current_stage == stage)
    if status:
        query = query.where(Invoice.status == status)
    if relationship_tier:
        query = query.join(Customer).where(Customer.relationship_tier == relationship_tier)

    query = query.order_by(desc(Invoice.risk_score), desc(Invoice.due_date)).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Registers a new receivable for recovery."""
    # Verify customer exists
    cust_res = await db.execute(select(Customer).where(Customer.id == payload.customer_id))
    customer = cust_res.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {payload.customer_id} does not exist"
        )

    now = datetime.now(timezone.utc)
    invoice = Invoice(
        customer_id=payload.customer_id,
        invoice_number=payload.invoice_number,
        amount_paise=payload.amount_paise,
        due_date=payload.due_date,
        razorpay_invoice_id=payload.razorpay_invoice_id,
        status=InvoiceStatus.PENDING,
        current_stage=RecoveryStage.INTAKE,
        current_level=1,
        valid_at=now,
        recorded_at=now,
    )
    db.add(invoice)

    customer.total_invoiced_paise += payload.amount_paise

    # Initial Audit Entry
    audit = AuditLog(
        invoice_id=invoice.id,
        event_type="INVOICE_INGESTED",
        actor="SYSTEM",
        action=f"Ingested receivable #{invoice.invoice_number} of ₹{invoice.amount_paise / 100:,.2f}",
        previous_state=None,
        new_state=InvoiceStatus.PENDING.value,
        recorded_at=now,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceDetailRead)
async def get_invoice_detail(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Returns deep-dive invoice details including bitemporal promises, audit trail, and communications."""
    query = (
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(
            selectinload(Invoice.customer),
            selectinload(Invoice.promises),
            selectinload(Invoice.payment_plans).selectinload(PaymentPlan.installments),
            selectinload(Invoice.communications),
            selectinload(Invoice.audit_logs),
            selectinload(Invoice.approvals),
        )
    )
    result = await db.execute(query)
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )
    return invoice


@router.post("/{invoice_id}/process", response_model=ProcessInvoiceResponse)
async def process_invoice_agent(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes an autonomous recovery cycle for an invoice using the LangGraph agent state machine.
    Runs diagnosis, policy evaluation, confidence gate, dynamic payment plan generation,
    Razorpay link generation, and communication dispatch.
    """
    query = (
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(
            selectinload(Invoice.customer),
            selectinload(Invoice.promises),
            selectinload(Invoice.communications),
        )
    )
    result = await db.execute(query)
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    customer = invoice.customer
    now = datetime.now(timezone.utc)
    days_overdue = max(0, (now.date() - invoice.due_date.date()).days)

    active_promises = [p for p in invoice.promises if p.status == PromiseStatus.ACTIVE]
    broken_promises = [p for p in invoice.promises if p.status == PromiseStatus.BROKEN]

    # Prepare LangGraph state
    initial_state = {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "customer_email": customer.email,
        "customer_phone": customer.phone,
        "amount_paise": invoice.amount_paise,
        "amount_paid_paise": invoice.amount_paid_paise,
        "due_date_str": invoice.due_date.strftime("%Y-%m-%d"),
        "days_overdue": days_overdue,
        "relationship_tier": customer.relationship_tier.value,
        "credit_score": customer.credit_score,
        "historical_recovery_rate": customer.historical_recovery_rate,
        "has_active_promise": len(active_promises) > 0,
        "has_broken_promise": len(broken_promises) > 0,
        "is_disputed": invoice.status == InvoiceStatus.DISPUTED or bool(invoice.dispute_reason),
        "current_level": invoice.current_level,
        "current_stage": invoice.current_stage.value,
        "confidence_score": invoice.confidence_score,
        "human_approved": True,  # Standard autonomous path
        "messages": [],
        "audit_trail": [],
    }

    # Execute LangGraph Agent
    final_state = await recovery_agent.ainvoke(initial_state)

    # Persist outputs back to DB
    invoice.risk_score = final_state.get("risk_score", invoice.risk_score)
    invoice.recovery_probability = final_state.get("recovery_probability", invoice.recovery_probability)
    invoice.current_level = final_state.get("current_level", invoice.current_level)
    invoice.current_stage = RecoveryStage(final_state.get("current_stage", "ACT"))
    if final_state.get("selected_tone"):
        invoice.optimal_tone = ToneType(final_state["selected_tone"])
    if final_state.get("payment_link_id"):
        invoice.active_razorpay_payment_link_id = final_state["payment_link_id"]
        invoice.active_payment_link_url = final_state["payment_link_url"]

    # Persist structured payment plan if offered
    if final_state.get("payment_plan_offered") and final_state.get("payment_plan_details"):
        plan_dict = final_state["payment_plan_details"]
        db_plan = PaymentPlan(
            invoice_id=invoice.id,
            total_amount_paise=plan_dict["total_amount_paise"],
            installment_count=plan_dict["installment_count"],
            frequency_days=plan_dict["frequency_days"],
            terms_summary=plan_dict["terms_summary"],
            status=plan_dict["status"],
            valid_at=now,
            recorded_at=now,
        )
        db.add(db_plan)
        await db.flush()

        for inst in plan_dict.get("installments", []):
            due_dt = datetime.fromisoformat(inst["due_date"]) if isinstance(inst["due_date"], str) else inst["due_date"]
            db_inst = PaymentPlanInstallment(
                payment_plan_id=db_plan.id,
                installment_number=inst["installment_number"],
                amount_paise=inst["amount_paise"],
                due_date=due_dt,
                razorpay_payment_link_id=inst.get("razorpay_payment_link_id"),
                status=inst.get("status", "PENDING"),
            )
            db.add(db_inst)

    # Persist Outbound Communication Record
    dispatched_content = final_state.get("last_message_content")
    if dispatched_content and final_state.get("current_stage") == "ACT":
        comm = Communication(
            invoice_id=invoice.id,
            channel=CommunicationChannel(final_state.get("selected_channel", "EMAIL")),
            direction=CommunicationDirection.OUTBOUND,
            sender="RevBack Autonomous Agent",
            recipient=customer.phone if final_state.get("selected_channel") in ("WHATSAPP", "SMS") and customer.phone else customer.email,
            subject=final_state.get("last_message_subject"),
            content=dispatched_content,
            intervention_level=final_state.get("current_level", 1),
            tone=ToneType(final_state.get("selected_tone", "COLLABORATIVE")),
            sent_at=now,
            valid_at=now,
            recorded_at=now,
        )
        db.add(comm)

    # Persist Audit Logs
    for entry in final_state.get("audit_trail", []):
        audit = AuditLog(
            invoice_id=invoice.id,
            event_type=entry.get("event_type", "AGENT_ACTION"),
            actor=entry.get("actor", "AGENT"),
            action=entry.get("action", "Recovery cycle step executed"),
            recorded_at=now,
        )
        db.add(audit)

    # Persist Human Approval Request if confidence gate triggered or level >= 6
    if final_state.get("requires_human_approval"):
        approval_type = (
            ApprovalType.CONFIDENCE_ESCALATION
            if final_state.get("approval_type") == "CONFIDENCE_ESCALATION"
            else ApprovalType.LEGAL_NOTICE
        )
        approval = HumanApproval(
            invoice_id=invoice.id,
            action_type=approval_type,
            proposed_action_details={
                "level": final_state.get("current_level"),
                "reason": final_state.get("approval_reason"),
                "message_draft": dispatched_content,
                "channel": final_state.get("selected_channel"),
            },
            confidence=final_state.get("confidence_score", invoice.confidence_score),
            threshold=0.85,
            status=ApprovalStatus.PENDING,
            requested_at=now,
        )
        db.add(approval)

    await db.commit()

    return ProcessInvoiceResponse(
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        current_stage=invoice.current_stage.value,
        current_level=invoice.current_level,
        risk_score=invoice.risk_score,
        recovery_probability=invoice.recovery_probability,
        selected_channel=final_state.get("selected_channel", "EMAIL"),
        selected_tone=final_state.get("selected_tone", "COLLABORATIVE"),
        payment_link_url=invoice.active_payment_link_url,
        requires_human_approval=final_state.get("requires_human_approval", False),
        approval_reason=final_state.get("approval_reason"),
        dispatched_message=dispatched_content,
    )


@router.post("/{invoice_id}/inbound-message", response_model=InboundMessageResponse)
async def ingest_inbound_message(
    invoice_id: str,
    payload: InboundMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingests an incoming debtor communication (e.g. Email or WhatsApp reply),
    runs LLM entity extraction & intent classification, tracks promises bitemporally,
    and adapts collection strategy.
    """
    query = (
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(selectinload(Invoice.customer), selectinload(Invoice.promises))
    )
    result = await db.execute(query)
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    now = datetime.now(timezone.utc)

    # 1. Record Inbound Communication
    inbound_comm = Communication(
        invoice_id=invoice.id,
        channel=CommunicationChannel(payload.channel),
        direction=CommunicationDirection.INBOUND,
        sender=payload.sender or invoice.customer.email,
        recipient="RevBack Inbound Gateway",
        content=payload.message,
        intervention_level=invoice.current_level,
        tone=ToneType.PROFESSIONAL,
        sent_at=now,
        valid_at=now,
        recorded_at=now,
    )
    db.add(inbound_comm)
    await db.flush()

    # 2. Extract Intent and Dispute
    intent_res = await DebtorExtractors.classify_intent(payload.message)
    dispute_res = await DebtorExtractors.extract_dispute(payload.message)
    promise_res = await DebtorExtractors.extract_promise(payload.message, invoice.amount_paise)

    action_taken = f"Classified as {intent_res.intent} (Confidence: {intent_res.confidence:.1%})"

    # 3. Handle Dispute Detection
    if dispute_res.is_disputed or intent_res.intent == "DISPUTE":
        invoice.status = InvoiceStatus.DISPUTED
        invoice.dispute_reason = dispute_res.reason or payload.message[:300]
        action_taken += f" | Dispute registered: {dispute_res.dispute_category}. Automated collections halted."

        audit = AuditLog(
            invoice_id=invoice.id,
            event_type="DISPUTE_RAISED",
            actor="DEBTOR",
            action=f"Debtor disputed invoice: {dispute_res.dispute_category}",
            previous_state=InvoiceStatus.PENDING.value,
            new_state=InvoiceStatus.DISPUTED.value,
            reasoning=dispute_res.reason,
            confidence_score=dispute_res.confidence,
            recorded_at=now,
        )
        db.add(audit)

    # 4. Handle Promise-to-Pay Extraction
    if promise_res.has_promise and promise_res.promised_amount_paise:
        promise_date_dt = (
            datetime.fromisoformat(promise_res.promise_date_iso)
            if promise_res.promise_date_iso
            else now
        )
        new_promise = Promise(
            invoice_id=invoice.id,
            promised_amount_paise=promise_res.promised_amount_paise,
            promise_date=promise_date_dt,
            status=PromiseStatus.ACTIVE,
            confidence=promise_res.confidence,
            raw_quote=promise_res.raw_quote,
            extracted_from_comm_id=inbound_comm.id,
            valid_at=now,
            recorded_at=now,
        )
        db.add(new_promise)
        invoice.current_stage = RecoveryStage.PROMISE_TRACKING
        action_taken += f" | Promise recorded: ₹{promise_res.promised_amount_paise / 100:,.2f} by {promise_date_dt.strftime('%Y-%m-%d')}"

        audit = AuditLog(
            invoice_id=invoice.id,
            event_type="PROMISE_RECORDED",
            actor="AGENT",
            action=f"Recorded commitment to pay ₹{promise_res.promised_amount_paise / 100:,.2f}",
            reasoning=f"Extracted from debtor quote: '{promise_res.raw_quote}'",
            confidence_score=promise_res.confidence,
            recorded_at=now,
        )
        db.add(audit)

    await db.commit()

    return InboundMessageResponse(
        invoice_id=invoice.id,
        intent=intent_res.intent,
        intent_confidence=intent_res.confidence,
        is_disputed=dispute_res.is_disputed,
        dispute_category=dispute_res.dispute_category,
        has_promise=promise_res.has_promise,
        promised_amount_paise=promise_res.promised_amount_paise,
        promise_date=promise_res.promise_date_iso,
        promise_confidence=promise_res.confidence,
        agent_action_taken=action_taken,
    )


@router.get("/{invoice_id}/evidence-bundle", response_model=Dict[str, Any])
async def get_evidence_bundle(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Compiles a complete, bitemporal legal evidentiary bundle for collections or litigation.
    Produces certifying statement, broken commitment timelines, and statutory notices.
    """
    query = (
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(
            selectinload(Invoice.customer),
            selectinload(Invoice.promises),
            selectinload(Invoice.communications),
            selectinload(Invoice.audit_logs),
        )
    )
    result = await db.execute(query)
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    audit_dicts = [
        {
            "event_type": a.event_type,
            "actor": a.actor,
            "action": a.action,
            "timestamp": a.recorded_at.isoformat(),
        }
        for a in invoice.audit_logs
    ]
    comm_dicts = [
        {
            "channel": c.channel.value,
            "direction": c.direction.value,
            "recipient": c.recipient,
            "content": c.content,
            "sent_at": c.sent_at.isoformat() if c.sent_at else None,
        }
        for c in invoice.communications
    ]
    promise_dicts = [
        {
            "amount_paise": p.promised_amount_paise,
            "promise_date": p.promise_date.isoformat(),
            "status": p.status.value,
            "valid_at": p.valid_at.isoformat(),
            "recorded_at": p.recorded_at.isoformat(),
        }
        for p in invoice.promises
    ]

    bundle = EvidenceBundler.compile_evidence_bundle(
        invoice_number=invoice.invoice_number,
        amount_paise=invoice.amount_paise,
        customer_name=invoice.customer.name,
        due_date_str=invoice.due_date.strftime("%Y-%m-%d"),
        audit_trail=audit_dicts,
        communications=comm_dicts,
        promises=promise_dicts,
    )
    return bundle
