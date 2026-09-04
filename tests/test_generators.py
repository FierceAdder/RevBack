"""Unit tests for MessageGenerator."""

from src.llm.generators import MessageGenerator
from src.models.db_models import CommunicationChannel, ToneType


def test_whatsapp_message_generation():
    """Generates friendly collaborative WhatsApp message with Razorpay link."""
    content, subject = MessageGenerator.generate_message(
        channel=CommunicationChannel.WHATSAPP,
        tone=ToneType.COLLABORATIVE,
        customer_name="TechCorp India",
        invoice_number="INV-1092",
        amount_paise=150_000_00,
        days_overdue=7,
        payment_link_url="https://rzp.io/i/mock123",
        due_date_str="2026-08-25",
    )
    assert subject is None
    assert "https://rzp.io/i/mock123" in content
    assert "₹150,000.00" in content
    assert "TechCorp India" in content


def test_formal_demand_notice_generation():
    """Generates formal demand notice with legal wording and statutory timeframe."""
    content, subject = MessageGenerator.generate_message(
        channel=CommunicationChannel.FORMAL_NOTICE,
        tone=ToneType.FORMAL_LEGAL,
        customer_name="Defaulter Enterprises",
        invoice_number="INV-9999",
        amount_paise=800_000_00,
        days_overdue=65,
        payment_link_url="https://rzp.io/i/legal_link",
        due_date_str="2026-07-01",
    )
    assert subject is not None
    assert "FORMAL DEMAND NOTICE" in subject
    assert "WITHOUT PREJUDICE" in content
    assert "seven (7) days" in content
    assert "https://rzp.io/i/legal_link" in content
