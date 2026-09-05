"""Human-in-the-loop Approval Queue Endpoints.

Allows supervisors and legal counsel to review, approve, reject, or edit
high-risk actions (formal legal notices, debt write-offs, low-confidence agent extractions).
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from src.db.session import get_db
from src.models.db_models import (
    HumanApproval, Invoice, Customer, Promise, Communication, AuditLog,
    ApprovalStatus, ApprovalType, RecoveryStage,
    InvoiceStatus, PromiseStatus, ToneType, CommunicationChannel, CommunicationDirection
)
from src.models.schemas import HumanApprovalRead
from src.agent.graph import recovery_agent


router = APIRouter(prefix="/approvals", tags=["Human Approvals"])


class ResolveApprovalRequest(BaseModel):
    decision: ApprovalStatus = Field(..., description="APPROVED, REJECTED, MODIFIED")
    reviewer_id: str = Field(default="supervisor@merchant.com")
    review_notes: Optional[str] = None
    override_action_details: Optional[Dict[str, Any]] = None


class ResolveApprovalResponse(BaseModel):
    approval_id: str
    invoice_id: str
    status: str
    reviewer_id: str
    resolved_at: str
    next_step: str
    dispatched: bool = False
    dispatched_channel: Optional[str] = None
    payment_link_url: Optional[str] = None


@router.get("", response_model=List[HumanApprovalRead])
async def list_approvals(
    status_filter: Optional[ApprovalStatus] = None,
    action_type: Optional[ApprovalType] = None,
    db: AsyncSession = Depends(get_db),
):
    """Lists human approval requests with optional status and action type filters."""
    query = select(HumanApproval).order_by(desc(HumanApproval.requested_at))
    if status_filter:
        query = query.where(HumanApproval.status == status_filter)
    if action_type:
        query = query.where(HumanApproval.action_type == action_type)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{approval_id}", response_model=HumanApprovalRead)
async def get_approval(
    approval_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetches a specific human approval request."""
    result = await db.execute(select(HumanApproval).where(HumanApproval.id == approval_id))
    approval = result.scalars().first()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
    return approval


@router.post("/{approval_id}/resolve", response_model=ResolveApprovalResponse)
async def resolve_approval(
    approval_id: str,
    payload: ResolveApprovalRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Supervisor resolution endpoint: APPROVE, REJECT, or MODIFY the escalation request.

    On APPROVED: Immediately resumes the LangGraph recovery agent for this invoice,
    generates a Razorpay payment link, and dispatches the approved communication.

    On REJECTED: Halts the escalation; receivable returns to monitoring.
    """
    query = (
        select(HumanApproval)
        .where(HumanApproval.id == approval_id)
        .options(
            selectinload(HumanApproval.invoice).selectinload(Invoice.customer),
            selectinload(HumanApproval.invoice).selectinload(Invoice.promises),
            selectinload(HumanApproval.invoice).selectinload(Invoice.communications),
        )
    )
    result = await db.execute(query)
    approval = result.scalars().first()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval request already resolved with status {approval.status.value}"
        )

    now = datetime.now(timezone.utc)
    approval.status = payload.decision
    approval.reviewer_id = payload.reviewer_id
    approval.review_notes = payload.review_notes
    approval.resolved_at = now

    invoice = approval.invoice
    next_step = ""
    dispatched = False
    dispatched_channel = None
    payment_link_url = None

    if payload.decision == ApprovalStatus.APPROVED and invoice:
        # ── Resume the full recovery agent for this invoice ──────────────────
        customer = invoice.customer
        days_overdue = max(0, (now.date() - invoice.due_date.date()).days)

        active_promises = [p for p in invoice.promises if p.status == PromiseStatus.ACTIVE]
        broken_promises = [p for p in invoice.promises if p.status == PromiseStatus.BROKEN]

        # Build state mirroring process_invoice_agent, but with human_approved=True
        # and the level from the approved action details
        approved_level = approval.proposed_action_details.get("level", invoice.current_level)
        approved_channel = approval.proposed_action_details.get("channel", "EMAIL")

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
            "current_level": approved_level,
            "current_stage": invoice.current_stage.value,
            "confidence_score": 1.0,  # Supervisor has explicitly approved — full confidence
            "human_approved": True,
            "requires_human_approval": False,  # Already approved, skip gate
            "messages": [],
            "audit_trail": [],
        }

        # Check if the graph has an interrupted checkpoint at human_approval_gate
        thread_id = invoice.agent_thread_id or f"inv_thread_{invoice.id}"
        agent_config = {"configurable": {"thread_id": thread_id}}
        is_interrupted = False
        try:
            snap = recovery_agent.get_state(agent_config)
            is_interrupted = bool(snap and snap.next and "human_approval_gate" in snap.next)
        except Exception:
            is_interrupted = False

        if is_interrupted:
            # Resume graph directly from checkpoint
            await recovery_agent.aupdate_state(agent_config, {"human_approved": True, "requires_human_approval": False})
            final_state = await recovery_agent.ainvoke(None, config=agent_config)
        else:
            # Execute full flow with explicit approval override
            final_state = await recovery_agent.ainvoke(initial_state, config=agent_config)

        # Persist agent outputs back to invoice
        invoice.risk_score = final_state.get("risk_score", invoice.risk_score)
        invoice.recovery_probability = final_state.get("recovery_probability", invoice.recovery_probability)
        invoice.current_level = final_state.get("current_level", invoice.current_level)
        invoice.current_stage = RecoveryStage.ESCALATION
        if final_state.get("selected_tone"):
            invoice.optimal_tone = ToneType(final_state["selected_tone"])
        if final_state.get("payment_link_id"):
            invoice.active_razorpay_payment_link_id = final_state["payment_link_id"]
            invoice.active_payment_link_url = final_state["payment_link_url"]
            payment_link_url = final_state["payment_link_url"]

        # Persist the dispatched outbound communication
        dispatched_content = final_state.get("last_message_content")
        selected_channel = final_state.get("selected_channel", approved_channel)
        if dispatched_content and final_state.get("current_stage") == "ACT":
            recipient = (
                customer.phone
                if selected_channel in ("WHATSAPP", "SMS") and customer.phone
                else customer.email
            )
            comm = Communication(
                invoice_id=invoice.id,
                channel=CommunicationChannel(selected_channel),
                direction=CommunicationDirection.OUTBOUND,
                sender="RevBack Autonomous Agent (Supervisor Approved)",
                recipient=recipient,
                subject=final_state.get("last_message_subject"),
                content=dispatched_content,
                intervention_level=final_state.get("current_level", approved_level),
                tone=ToneType(final_state.get("selected_tone", "PROFESSIONAL")),
                sent_at=now,
                valid_at=now,
                recorded_at=now,
            )
            db.add(comm)
            dispatched = True
            dispatched_channel = selected_channel

        # Persist agent audit logs
        for entry in final_state.get("audit_trail", []):
            audit_entry = AuditLog(
                invoice_id=invoice.id,
                event_type=entry.get("event_type", "AGENT_ACTION"),
                actor=entry.get("actor", "AGENT"),
                action=entry.get("action", "Supervisor-approved recovery step executed"),
                recorded_at=now,
            )
            db.add(audit_entry)

        next_step = (
            f"Supervisor-approved intervention executed. "
            f"{'Formal notice dispatched via ' + selected_channel + '.' if dispatched else 'Agent ran but no message generated.'} "
            f"{'Razorpay link: ' + payment_link_url if payment_link_url else ''}"
        )

    elif payload.decision == ApprovalStatus.REJECTED:
        next_step = "Escalation rejected by supervisor. Receivable returned to monitoring queue."
        # Update invoice to reflect halted escalation
        if invoice and invoice.current_stage == RecoveryStage.ESCALATION:
            invoice.current_stage = RecoveryStage.ACT

        # Terminate graph thread if paused at approval gate
        thread_id = invoice.agent_thread_id or f"inv_thread_{invoice.id}"
        agent_config = {"configurable": {"thread_id": thread_id}}
        try:
            snap = recovery_agent.get_state(agent_config)
            if snap and snap.next and "human_approval_gate" in snap.next:
                await recovery_agent.aupdate_state(agent_config, {"human_approved": False, "requires_human_approval": False})
                await recovery_agent.ainvoke(None, config=agent_config)
        except Exception:
            pass

    elif payload.decision == ApprovalStatus.MODIFIED:
        next_step = "Intervention modified. Applying customized supervisor terms."
        if payload.override_action_details:
            approval.proposed_action_details = payload.override_action_details

    # Log immutable supervisor action
    audit = AuditLog(
        invoice_id=approval.invoice_id,
        event_type="HUMAN_APPROVAL_RESOLVED",
        actor="HUMAN_SUPERVISOR",
        action=f"Supervisor {payload.reviewer_id} {payload.decision.value} {approval.action_type.value}. {next_step}",
        reasoning=payload.review_notes or "Supervisor decision recorded.",
        confidence_score=1.0,
        recorded_at=now,
    )
    db.add(audit)
    await db.commit()

    return ResolveApprovalResponse(
        approval_id=approval.id,
        invoice_id=approval.invoice_id,
        status=approval.status.value,
        reviewer_id=payload.reviewer_id,
        resolved_at=now.isoformat(),
        next_step=next_step,
        dispatched=dispatched,
        dispatched_channel=dispatched_channel,
        payment_link_url=payment_link_url,
    )

