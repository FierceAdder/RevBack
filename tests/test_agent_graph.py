"""Integration tests for LangGraph Recovery Agent, Tools, and Payment Plans."""

import pytest
from src.agent.graph import build_recovery_graph
from src.agent.payment_plans import PaymentPlanEngine
from src.agent.channels import ChannelDispatcher
from src.agent.tools import EvidenceBundler
from src.models.db_models import CommunicationChannel


@pytest.mark.asyncio
async def test_standard_invoice_agent_cycle():
    """Verifies complete autonomous execution cycle for an overdue invoice."""
    agent = build_recovery_graph(interrupt_human=False)

    initial_state = {
        "invoice_id": "inv_001",
        "customer_id": "cust_001",
        "customer_name": "Bharat Retailers Pvt Ltd",
        "customer_email": "accounts@bharatretail.in",
        "customer_phone": "+919876543210",
        "invoice_number": "INV-2026-901",
        "amount_paise": 150_000_00,  # ₹1.5 Lakhs
        "amount_paid_paise": 0,
        "due_date_str": "2026-08-20",
        "days_overdue": 12,
        "relationship_tier": "STANDARD",
        "credit_score": 720,
        "historical_recovery_rate": 0.88,
        "current_stage": "INTAKE",
        "current_level": 1,
        "is_recovered": False,
        "is_disputed": False,
        "dispute_reason": None,
        "has_active_promise": False,
        "has_broken_promise": False,
        "confidence_score": 0.95,
        "messages": [],
        "audit_trail": [],
    }

    final_state = await agent.ainvoke(initial_state)

    # Verify State progression
    assert final_state["current_stage"] == "ACT"
    assert final_state["current_level"] == 2
    assert final_state["risk_score"] > 0
    assert final_state["recovery_probability"] > 0.50
    assert "https://rzp.io/" in final_state["payment_link_url"]
    assert len(final_state["messages"]) == 1
    assert len(final_state["audit_trail"]) >= 4
    assert final_state["messages"][0]["delivery_status"] == "DELIVERED"


@pytest.mark.asyncio
async def test_payment_plan_generation_at_level_4():
    """Verifies structured installment plan is generated when agent acts at Level 4."""
    agent = build_recovery_graph(interrupt_human=False)

    initial_state = {
        "invoice_id": "inv_002",
        "customer_id": "cust_002",
        "customer_name": "Apex Logistics",
        "customer_email": "finance@apex.in",
        "customer_phone": "+919123456780",
        "invoice_number": "INV-2026-902",
        "amount_paise": 300_000_00,  # ₹3 Lakhs
        "amount_paid_paise": 0,
        "due_date_str": "2026-07-25",
        "days_overdue": 35,
        "relationship_tier": "STANDARD",
        "credit_score": 650,
        "historical_recovery_rate": 0.75,
        "current_stage": "DIAGNOSE",
        "current_level": 3,  # Will advance to Level 4
        "is_recovered": False,
        "is_disputed": False,
        "dispute_reason": None,
        "has_active_promise": False,
        "has_broken_promise": False,
        "confidence_score": 0.92,
        "messages": [],
        "audit_trail": [],
    }

    final_state = await agent.ainvoke(initial_state)

    assert final_state["current_level"] == 4
    assert final_state["payment_plan_offered"] is True
    assert final_state["payment_plan_details"] is not None
    installments = final_state["payment_plan_details"]["installments"]
    assert len(installments) == 3
    assert sum(i["amount_paise"] for i in installments) == 300_000_00


@pytest.mark.asyncio
async def test_confidence_gating_triggers_human_approval():
    """Uncertain extraction (confidence 0.65) triggers human approval gate."""
    agent = build_recovery_graph(interrupt_human=False)

    initial_state = {
        "invoice_id": "inv_003",
        "customer_id": "cust_003",
        "customer_name": "Uncertain Corp",
        "customer_email": "pay@uncertain.in",
        "customer_phone": "+919888888888",
        "invoice_number": "INV-2026-903",
        "amount_paise": 200_000_00,
        "amount_paid_paise": 0,
        "due_date_str": "2026-08-10",
        "days_overdue": 20,
        "relationship_tier": "STANDARD",
        "credit_score": 700,
        "historical_recovery_rate": 0.80,
        "current_stage": "INTAKE",
        "current_level": 1,
        "is_recovered": False,
        "is_disputed": False,
        "dispute_reason": None,
        "has_active_promise": False,
        "has_broken_promise": False,
        "confidence_score": 0.65,  # Below 0.80 threshold
        "messages": [],
        "audit_trail": [],
    }

    final_state = await agent.ainvoke(initial_state)

    assert final_state["confidence_gate_passed"] is False
    assert final_state["requires_human_approval"] is True
    assert final_state["approval_type"] == "CONFIDENCE_ESCALATION"
    # Verify human approval node was evaluated
    assert any(a["event_type"] == "HUMAN_REVIEW_RESOLVED" for a in final_state["audit_trail"])


@pytest.mark.asyncio
async def test_disputed_invoice_halts_before_dispatch():
    """Disputed invoice halts immediately without dispatching communications."""
    agent = build_recovery_graph(interrupt_human=False)

    initial_state = {
        "invoice_id": "inv_004",
        "customer_id": "cust_004",
        "customer_name": "Disputed Client",
        "customer_email": "dispute@client.in",
        "customer_phone": "+919777777777",
        "invoice_number": "INV-2026-904",
        "amount_paise": 200_000_00,
        "amount_paid_paise": 0,
        "due_date_str": "2026-08-01",
        "days_overdue": 30,
        "relationship_tier": "STANDARD",
        "credit_score": 700,
        "historical_recovery_rate": 0.80,
        "current_stage": "INTAKE",
        "current_level": 2,
        "is_recovered": False,
        "is_disputed": True,  # Disputed!
        "dispute_reason": "Billed amount does not match purchase order",
        "has_active_promise": False,
        "has_broken_promise": False,
        "confidence_score": 0.95,
        "messages": [],
        "audit_trail": [],
    }

    final_state = await agent.ainvoke(initial_state)

    assert final_state["should_act"] is False
    assert len(final_state["messages"]) == 0  # No message dispatched!


def test_channel_dispatcher_fallback():
    """WhatsApp target falls back to Email when debtor phone is missing."""
    resolved, note = ChannelDispatcher.resolve_channel(
        target_channel=CommunicationChannel.WHATSAPP,
        has_email=True,
        has_phone=False,
    )
    assert resolved == CommunicationChannel.EMAIL
    assert "gracefully fell back to EMAIL" in note


def test_evidence_bundle_generation():
    """Evidence Bundler outputs structured legal audit trail."""
    bundle = EvidenceBundler.compile_evidence_bundle(
        invoice_number="INV-2026-999",
        amount_paise=500_000_00,
        customer_name="Delta Services",
        due_date_str="2026-07-01",
        audit_trail=[{"event": "PROMISE_BROKEN", "timestamp": "2026-08-15T10:00:00Z"}],
        communications=[{"channel": "FORMAL_NOTICE", "content": "Statutory demand"}],
        promises=[{"amount": 50000000, "status": "BROKEN"}],
    )
    assert bundle["evidence_bundle_id"] == "EV-BUNDLE-INV-2026-999"
    assert bundle["unkept_commitments_count"] == 1
    assert "bitemporal ledger" in bundle["certifying_statement"]
