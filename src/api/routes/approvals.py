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
    HumanApproval, Invoice, AuditLog, ApprovalStatus, ApprovalType, RecoveryStage
)
from src.models.schemas import HumanApprovalRead


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
    Resumes or halts the agent workflow accordingly.
    """
    query = (
        select(HumanApproval)
        .where(HumanApproval.id == approval_id)
        .options(selectinload(HumanApproval.invoice))
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

    if payload.decision == ApprovalStatus.APPROVED:
        next_step = f"Intervention approved. Proceeding with Level {approval.proposed_action_details.get('level', 6)} action."
        if invoice:
            invoice.current_stage = RecoveryStage.ESCALATION
    elif payload.decision == ApprovalStatus.REJECTED:
        next_step = "Intervention rejected. Escalation halted; receivable returned to monitoring."
    elif payload.decision == ApprovalStatus.MODIFIED:
        next_step = "Intervention modified. Applying customized supervisor terms."
        if payload.override_action_details:
            approval.proposed_action_details = payload.override_action_details

    # Log immutable supervisor action
    audit = AuditLog(
        invoice_id=approval.invoice_id,
        event_type="HUMAN_APPROVAL_RESOLVED",
        actor="HUMAN_SUPERVISOR",
        action=f"Supervisor {payload.reviewer_id} {payload.decision.value} {approval.action_type.value}",
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
    )
