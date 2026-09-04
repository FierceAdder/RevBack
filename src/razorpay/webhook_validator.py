"""Razorpay Webhook Signature Validator and Event Parser.

Enforces HMAC-SHA256 signature verification to ensure authentic callbacks from Razorpay.
"""

import hashlib
import hmac
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from src.config import settings


class ParsedPaymentEvent(BaseModel):
    event: str = Field(..., description="Razorpay event type (e.g. payment_link.paid)")
    payment_id: Optional[str] = None
    payment_link_id: Optional[str] = None
    razorpay_invoice_id: Optional[str] = None
    amount_paise: int = 0
    status: str = "captured"
    customer_email: Optional[str] = None
    customer_contact: Optional[str] = None
    notes: Dict[str, Any] = Field(default_factory=dict)
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class RazorpayWebhookValidator:
    """Validates and parses incoming Razorpay webhook payloads."""

    @classmethod
    def verify_signature(
        cls,
        payload_body: bytes,
        signature: Optional[str],
        secret: Optional[str] = None,
    ) -> bool:
        """
        Verifies HMAC-SHA256 signature against Razorpay webhook secret.
        """
        if not signature:
            return False

        webhook_secret = secret or settings.RAZORPAY_WEBHOOK_SECRET
        if not webhook_secret:
            return False

        try:
            expected_signature = hmac.new(
                key=webhook_secret.encode("utf-8"),
                msg=payload_body,
                digestmod=hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False

    @classmethod
    def parse_event(cls, payload: Dict[str, Any]) -> ParsedPaymentEvent:
        """
        Extracts key financial reconciliation data from Razorpay webhook JSON payload.
        Handles payment_link.paid, invoice.paid, payment.captured.
        """
        event_type = payload.get("event", "unknown")
        entity_container = payload.get("payload", {})

        payment_id = None
        payment_link_id = None
        invoice_id = None
        amount_paise = 0
        email = None
        contact = None
        notes = {}
        status = "captured"

        # 1. Handle payment_link.paid
        if "payment_link" in entity_container:
            link_entity = entity_container["payment_link"].get("entity", {})
            payment_link_id = link_entity.get("id")
            amount_paise = link_entity.get("amount_paid") or link_entity.get("amount") or 0
            customer_info = link_entity.get("customer", {})
            email = customer_info.get("email")
            contact = customer_info.get("contact")
            notes = link_entity.get("notes", {})
            status = link_entity.get("status", "paid")

        # 2. Extract payment entity if included
        if "payment" in entity_container:
            payment_entity = entity_container["payment"].get("entity", {})
            payment_id = payment_entity.get("id")
            if not amount_paise:
                amount_paise = payment_entity.get("amount", 0)
            email = email or payment_entity.get("email")
            contact = contact or payment_entity.get("contact")
            notes = notes or payment_entity.get("notes", {})
            status = payment_entity.get("status", status)

        # 3. Handle invoice.paid
        if "invoice" in entity_container:
            inv_entity = entity_container["invoice"].get("entity", {})
            invoice_id = inv_entity.get("id")
            if not amount_paise:
                amount_paise = inv_entity.get("amount_paid", 0)

        return ParsedPaymentEvent(
            event=event_type,
            payment_id=payment_id,
            payment_link_id=payment_link_id,
            razorpay_invoice_id=invoice_id,
            amount_paise=amount_paise,
            status=status,
            customer_email=email,
            customer_contact=contact,
            notes=notes,
            raw_payload=payload,
        )
