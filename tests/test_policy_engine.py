"""Unit tests for PolicyEngine."""

from datetime import datetime, timezone, timedelta
from src.engine.policy import PolicyEngine
from src.models.db_models import RelationshipTier, CommunicationChannel, ToneType


def test_disputed_invoice_halts_action():
    """Disputed invoices must immediately halt outreach and route to human."""
    decision = PolicyEngine.evaluate_next_action(
        current_level=2,
        days_overdue=10,
        last_contact_time=None,
        has_active_promise=False,
        has_broken_promise=False,
        is_disputed=True,
        amount_paise=100_000_00,
    )
    assert decision.should_act is False
    assert decision.requires_human_approval is True
    assert "disputed" in decision.reason.lower()


def test_active_promise_suspends_reminders():
    """Active promise in progress suspends automated messaging."""
    decision = PolicyEngine.evaluate_next_action(
        current_level=2,
        days_overdue=12,
        last_contact_time=None,
        has_active_promise=True,
        has_broken_promise=False,
        is_disputed=False,
        amount_paise=100_000_00,
    )
    assert decision.should_act is False
    assert "promise" in decision.reason.lower()


def test_cooldown_enforcement():
    """Contact attempts inside cooldown window must be rejected."""
    now = datetime.now(timezone.utc)
    last_contact = now - timedelta(days=1)  # Only 1 day ago; Level 2 needs 3 days

    decision = PolicyEngine.evaluate_next_action(
        current_level=2,
        days_overdue=15,
        last_contact_time=last_contact,
        has_active_promise=False,
        has_broken_promise=False,
        is_disputed=False,
        amount_paise=100_000_00,
        now=now,
    )
    assert decision.should_act is False
    assert decision.cooldown_remaining_hours > 0


def test_broken_promise_accelerates_escalation():
    """Broken promises bypass cooldown and advance 2 levels."""
    now = datetime.now(timezone.utc)
    last_contact = now - timedelta(hours=12)

    decision = PolicyEngine.evaluate_next_action(
        current_level=2,
        days_overdue=20,
        last_contact_time=last_contact,
        has_active_promise=False,
        has_broken_promise=True,
        is_disputed=False,
        amount_paise=200_000_00,
        now=now,
    )
    assert decision.should_act is True
    assert decision.next_level == 4  # 2 + 2
    assert decision.tone == ToneType.FIRM


def test_legal_notice_requires_human_approval():
    """Advancing to Level 6 (Formal Legal Notice) requires human sign-off."""
    now = datetime.now(timezone.utc)
    last_contact = now - timedelta(days=6)

    decision = PolicyEngine.evaluate_next_action(
        current_level=5,
        days_overdue=60,
        last_contact_time=last_contact,
        has_active_promise=False,
        has_broken_promise=False,
        is_disputed=False,
        amount_paise=600_000_00,  # ₹6 Lakhs
        now=now,
    )
    assert decision.should_act is True
    assert decision.next_level == 6
    assert decision.requires_human_approval is True
    assert decision.channel == CommunicationChannel.FORMAL_NOTICE
