"""Unit & Integration Tests for Razorpay Webhook Processing and Signature Verification."""

from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import json
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.models.db_models import (
    Customer, Invoice, Promise, AuditLog, InvoiceStatus, RecoveryStage,
    RelationshipTier, PromiseStatus
)
from src.razorpay.webhook_validator import RazorpayWebhookValidator


def generate_test_signature(payload_bytes: bytes, secret: str = None) -> str:
    webhook_secret = secret or settings.RAZORPAY_WEBHOOK_SECRET
    return hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()


def test_signature_validator_unit():
    """Unit test for RazorpayWebhookValidator logic."""
    body = b'{"event": "payment_link.paid"}'
    valid_sig = generate_test_signature(body)

    assert RazorpayWebhookValidator.verify_signature(body, valid_sig) is True
    assert RazorpayWebhookValidator.verify_signature(body, "invalid_sig") is False
    assert RazorpayWebhookValidator.verify_signature(body, None) is False


@pytest.mark.asyncio
async def test_webhook_rejects_missing_signature(client: AsyncClient):
    """Webhook endpoint rejects requests without signature header."""
    response = await client.post(
        "/api/v1/webhooks/razorpay",
        content=json.dumps({"event": "payment.captured"}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert "signature" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_webhook_rejects_tampered_signature(client: AsyncClient):
    """Webhook endpoint rejects requests with altered payload or bad signature."""
    payload_bytes = json.dumps({"event": "payment_link.paid", "amount": 5000}).encode("utf-8")
    tampered_sig = generate_test_signature(b"altered_content")

    response = await client.post(
        "/api/v1/webhooks/razorpay",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": tampered_sig,
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_payment_link_paid_reconciles_invoice(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """
    Simulates authentic Razorpay payment_link.paid event.
    Verifies invoice transitions to PAID & RECOVERED, active promises mark KEPT,
    and audit log records reconciliation.
    """
    now = datetime.now(timezone.utc)

    # 1. Setup Customer, Invoice, and Active Promise
    customer = Customer(
        name="Nexus Infotech India",
        email="finance@nexusinfo.in",
        relationship_tier=RelationshipTier.STANDARD,
        total_invoiced_paise=150_000_00,
        total_recovered_paise=0,
    )
    db_session.add(customer)
    await db_session.flush()

    invoice = Invoice(
        customer_id=customer.id,
        invoice_number="INV-RZP-9001",
        amount_paise=150_000_00,
        amount_paid_paise=0,
        due_date=now - timedelta(days=15),
        status=InvoiceStatus.PENDING,
        current_stage=RecoveryStage.PROMISE_TRACKING,
        current_level=2,
        active_razorpay_payment_link_id="plink_test_9001",
        active_payment_link_url="https://rzp.io/i/plink_test_9001",
    )
    db_session.add(invoice)
    await db_session.flush()

    promise = Promise(
        invoice_id=invoice.id,
        promised_amount_paise=150_000_00,
        promise_date=now + timedelta(days=2),
        status=PromiseStatus.ACTIVE,
        confidence=0.95,
        raw_quote="We will transfer via link today.",
    )
    db_session.add(promise)
    await db_session.commit()

    # 2. Build authentic Razorpay payment_link.paid webhook payload
    webhook_payload = {
        "entity": "event",
        "event": "payment_link.paid",
        "contains": ["payment_link", "payment"],
        "payload": {
            "payment_link": {
                "entity": {
                    "id": "plink_test_9001",
                    "amount": 150_000_00,
                    "amount_paid": 150_000_00,
                    "status": "paid",
                    "customer": {
                        "name": "Nexus Infotech India",
                        "email": "finance@nexusinfo.in",
                    },
                    "notes": {
                        "invoice_number": "INV-RZP-9001",
                    },
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_test_998877",
                    "amount": 150_000_00,
                    "status": "captured",
                    "method": "upi",
                }
            },
        },
    }

    payload_bytes = json.dumps(webhook_payload).encode("utf-8")
    signature = generate_test_signature(payload_bytes)

    # 3. Post to Webhook Endpoint
    response = await client.post(
        "/api/v1/webhooks/razorpay",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
        },
    )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["amount_recovered_paise"] == 150_000_00
    assert res_data["stage"] == "RECOVERED"

    # 4. Verify Database State
    inv_res = await db_session.execute(select(Invoice).where(Invoice.id == invoice.id))
    updated_inv = inv_res.scalars().first()
    assert updated_inv.status == InvoiceStatus.PAID
    assert updated_inv.current_stage == RecoveryStage.RECOVERED
    assert updated_inv.amount_paid_paise == 150_000_00

    prom_res = await db_session.execute(select(Promise).where(Promise.id == promise.id))
    updated_prom = prom_res.scalars().first()
    assert updated_prom.status == PromiseStatus.KEPT

    cust_res = await db_session.execute(select(Customer).where(Customer.id == customer.id))
    updated_cust = cust_res.scalars().first()
    assert updated_cust.total_recovered_paise == 150_000_00
    assert updated_cust.historical_recovery_rate == 1.0

    audit_res = await db_session.execute(
        select(AuditLog).where(AuditLog.invoice_id == invoice.id, AuditLog.event_type == "PAYMENT_RECEIVED")
    )
    audit = audit_res.scalars().first()
    assert audit is not None
    assert audit.actor == "RAZORPAY_WEBHOOK"
    assert "₹150,000.00" in audit.action
