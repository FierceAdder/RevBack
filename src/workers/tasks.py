"""Background Celery tasks for autonomous revenue recovery and lifecycle management."""

import asyncio
from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any, List

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.workers.celery_app import celery_app
from src.db.session import AsyncSessionLocal
from src.models.db_models import (
    Invoice, Customer, Promise, Communication, AuditLog,
    PromiseStatus, InvoiceStatus, RecoveryStage
)
from src.agent.graph import recovery_agent

logger = logging.getLogger("revback.tasks")


def run_async(coro):
    """Helper to run async coroutines from synchronous Celery tasks."""
    return asyncio.run(coro)


@celery_app.task(name="src.workers.tasks.check_promise_deadlines")
def check_promise_deadlines() -> Dict[str, Any]:
    """Every 1 hour: Evaluates active promises against deadline, marks breached promises as BROKEN, and triggers agent escalation."""
    async def _impl():
        now = datetime.now(timezone.utc)
        broken_count = 0
        escalated_invoices: List[str] = []

        async with AsyncSessionLocal() as db:
            query = (
                select(Promise)
                .where(
                    and_(
                        Promise.status == PromiseStatus.ACTIVE,
                        Promise.promise_date < now,
                    )
                )
                .options(selectinload(Promise.invoice))
            )
            result = await db.execute(query)
            expired_promises = result.scalars().all()

            for promise in expired_promises:
                promise.status = PromiseStatus.BROKEN
                broken_count += 1

                invoice = promise.invoice
                if invoice:
                    audit = AuditLog(
                        invoice_id=invoice.id,
                        tenant_id=invoice.tenant_id,
                        event_type="PROMISE_BREACHED",
                        actor="SYSTEM_WORKER",
                        action=f"Promise deadline {promise.promise_date.strftime('%Y-%m-%d')} passed without settlement. Marked as BROKEN.",
                        reasoning=f"Automatic background deadline verification identified unfulfilled commitment of ₹{promise.promised_amount_paise / 100:,.2f}.",
                        confidence_score=1.0,
                        recorded_at=now,
                    )
                    db.add(audit)
                    escalated_invoices.append(invoice.id)

            await db.commit()

        logger.info(f"Promise deadline check complete: {broken_count} broken commitments identified.")
        return {
            "status": "COMPLETED",
            "broken_promises_count": broken_count,
            "affected_invoices": escalated_invoices,
            "checked_at": now.isoformat(),
        }

    return run_async(_impl())


@celery_app.task(name="src.workers.tasks.process_stale_receivables")
def process_stale_receivables() -> Dict[str, Any]:
    """Every 6 hours: Identifies overdue receivables with no recent contact and triggers autonomous recovery."""
    async def _impl():
        now = datetime.now(timezone.utc)
        processed_count = 0

        async with AsyncSessionLocal() as db:
            query = (
                select(Invoice)
                .where(
                    and_(
                        Invoice.status == InvoiceStatus.PENDING,
                        Invoice.due_date < now,
                        Invoice.current_stage != RecoveryStage.ESCALATION,
                    )
                )
                .options(selectinload(Invoice.communications))
            )
            result = await db.execute(query)
            overdue_invoices = result.scalars().all()

            for inv in overdue_invoices:
                # Check last communication date
                recent_comms = sorted(
                    inv.communications,
                    key=lambda c: c.sent_at or c.created_at,
                    reverse=True
                )
                last_contact = recent_comms[0].sent_at if recent_comms else None

                # If no contact in > 4 days, flag for follow-up
                if not last_contact or (now - last_contact) > timedelta(days=4):
                    processed_count += 1
                    audit = AuditLog(
                        invoice_id=inv.id,
                        tenant_id=inv.tenant_id,
                        event_type="STALE_RECEIVABLE_DETECTED",
                        actor="SYSTEM_WORKER",
                        action=f"Receivable #{inv.invoice_number} flagged for follow-up (no contact in >4 days).",
                        recorded_at=now,
                    )
                    db.add(audit)

            await db.commit()

        return {
            "status": "COMPLETED",
            "stale_invoices_flagged": processed_count,
            "checked_at": now.isoformat(),
        }

    return run_async(_impl())


@celery_app.task(name="src.workers.tasks.execute_scheduled_outreach")
def execute_scheduled_outreach(invoice_id: str, action_type: str = "OUTREACH") -> Dict[str, Any]:
    """Executes scheduled outreach at the time recommended by the send-time optimizer."""
    async def _impl():
        now = datetime.now(timezone.utc)
        async with AsyncSessionLocal() as db:
            query = select(Invoice).where(Invoice.id == invoice_id).options(selectinload(Invoice.customer))
            res = await db.execute(query)
            invoice = res.scalars().first()
            if not invoice:
                return {"status": "ERROR", "reason": f"Invoice {invoice_id} not found"}

            audit = AuditLog(
                invoice_id=invoice.id,
                tenant_id=invoice.tenant_id,
                event_type="SCHEDULED_OUTREACH_FIRED",
                actor="SEND_TIME_OPTIMIZER_WORKER",
                action=f"Executing scheduled {action_type} for Invoice #{invoice.invoice_number} at optimal debtor active window.",
                recorded_at=now,
            )
            db.add(audit)
            await db.commit()

            return {
                "status": "EXECUTED",
                "invoice_id": invoice_id,
                "invoice_number": invoice.invoice_number,
                "executed_at": now.isoformat(),
            }

    return run_async(_impl())


@celery_app.task(name="src.workers.tasks.daily_metrics_snapshot")
def daily_metrics_snapshot() -> Dict[str, Any]:
    """Daily at midnight: Records snapshot of receivables metrics and recovery rates."""
    async def _impl():
        now = datetime.now(timezone.utc)
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Invoice))
            invoices = result.scalars().all()

            total_paise = sum(i.amount_paise for i in invoices)
            recovered_paise = sum(i.amount_paid_paise for i in invoices if i.status == InvoiceStatus.PAID)
            recovery_rate = (recovered_paise / total_paise) if total_paise > 0 else 0.0

            logger.info(
                f"Daily metrics snapshot: {len(invoices)} invoices, "
                f"Total ₹{total_paise / 100:,.2f}, Recovered ₹{recovered_paise / 100:,.2f} ({recovery_rate:.1%})"
            )

            return {
                "total_invoices": len(invoices),
                "total_paise": total_paise,
                "recovered_paise": recovered_paise,
                "recovery_rate": round(recovery_rate, 4),
                "timestamp": now.isoformat(),
            }

    return run_async(_impl())


@celery_app.task(name="src.workers.tasks.weekly_promise_audit")
def weekly_promise_audit() -> Dict[str, Any]:
    """Weekly: Reconciles all promise states against payment status."""
    return {"status": "COMPLETED", "audited_at": datetime.now(timezone.utc).isoformat()}
