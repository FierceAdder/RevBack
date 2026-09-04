"""Razorpay Webhook Handler Endpoint.

Secured with HMAC-SHA256 signature verification. Reconciles real-time payments,
updates invoice stages, marks promises KEPT, and records audit logs.
"""

from datetime import datetime, timezone
import json
from typing import Dict, Any
from fastapi import APIRouter, Request, Header, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_db
from src.models.db_models import (
    Invoice, InvoiceStatus, RecoveryStage, Promise, PromiseStatus,
    PaymentPlan, PaymentPlanInstallment, AuditLog, Customer
)
from src.razorpay.webhook_validator import RazorpayWebhookValidator


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/razorpay", status_code=status.HTTP_200_OK)
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None, alias="X-Razorpay-Signature"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Receives and processes authenticated Razorpay webhook events:
    - payment_link.paid
    - payment.captured
    - invoice.paid
    """
    raw_body = await request.body()

    # 1. Verify HMAC Signature
    is_valid = RazorpayWebhookValidator.verify_signature(
        payload_body=raw_body,
        signature=x_razorpay_signature,
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing Razorpay webhook signature (HMAC verification failed)"
        )

    # 2. Parse Event
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON body"
        )

    parsed = RazorpayWebhookValidator.parse_event(payload)

    # 3. Handle Supported Payment Events
    if parsed.event in ("payment_link.paid", "payment.captured", "invoice.paid"):
        # Match invoice by payment link id or invoice number in notes
        query = select(Invoice)
        if parsed.payment_link_id:
            query = query.where(Invoice.active_razorpay_payment_link_id == parsed.payment_link_id)
        elif parsed.notes.get("invoice_number"):
            query = query.where(Invoice.invoice_number == parsed.notes["invoice_number"])
        elif parsed.razorpay_invoice_id:
            query = query.where(Invoice.razorpay_invoice_id == parsed.razorpay_invoice_id)

        result = await db.execute(query)
        invoice = result.scalars().first()

        if invoice:
            now = datetime.now(timezone.utc)
            invoice.amount_paid_paise += parsed.amount_paise

            # Check if fully recovered
            if invoice.amount_paid_paise >= invoice.amount_paise:
                invoice.status = InvoiceStatus.PAID
                invoice.current_stage = RecoveryStage.RECOVERED
            else:
                invoice.status = InvoiceStatus.PARTIALLY_PAID

            # Reconcile Promises to KEPT
            promise_res = await db.execute(
                select(Promise).where(
                    Promise.invoice_id == invoice.id,
                    Promise.status == PromiseStatus.ACTIVE
                )
            )
            for active_promise in promise_res.scalars().all():
                active_promise.status = PromiseStatus.KEPT
                active_promise.recorded_at = now

            # Reconcile Payment Plan Installments if applicable
            plan_res = await db.execute(
                select(PaymentPlan).where(PaymentPlan.invoice_id == invoice.id)
            )
            for plan in plan_res.scalars().all():
                inst_res = await db.execute(
                    select(PaymentPlanInstallment).where(
                        PaymentPlanInstallment.payment_plan_id == plan.id,
                        PaymentPlanInstallment.status == "PENDING"
                    )
                )
                installment = inst_res.scalars().first()
                if installment:
                    installment.status = "PAID"
                    installment.paid_at = now

            # Update Customer Lifetime Stats
            cust_res = await db.execute(select(Customer).where(Customer.id == invoice.customer_id))
            customer = cust_res.scalars().first()
            if customer:
                customer.total_recovered_paise += parsed.amount_paise
                if customer.total_invoiced_paise > 0:
                    customer.historical_recovery_rate = min(
                        1.0, customer.total_recovered_paise / customer.total_invoiced_paise
                    )

            # Record Immutable Audit Trail
            audit_log = AuditLog(
                invoice_id=invoice.id,
                event_type="PAYMENT_RECEIVED",
                actor="RAZORPAY_WEBHOOK",
                action=f"Reconciled ₹{parsed.amount_paise / 100:,.2f} via {parsed.event} (Tx: {parsed.payment_id or 'N/A'})",
                previous_state=invoice.status.value,
                new_state=invoice.status.value,
                reasoning=f"Automatic webhook reconciliation from Razorpay event: {parsed.event}",
                confidence_score=1.0,
                token_cost_usd=0.0,
                metadata_json={
                    "event": parsed.event,
                    "payment_id": parsed.payment_id,
                    "payment_link_id": parsed.payment_link_id,
                    "amount_paise": parsed.amount_paise,
                },
                recorded_at=now,
            )
            db.add(audit_log)
            await db.commit()

            return {
                "status": "success",
                "message": f"Payment reconciled for Invoice #{invoice.invoice_number}",
                "invoice_id": invoice.id,
                "amount_recovered_paise": parsed.amount_paise,
                "stage": invoice.current_stage.value,
            }

    return {
        "status": "acknowledged",
        "event": parsed.event,
        "message": "Webhook received but no matching active receivable required action",
    }
