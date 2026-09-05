"""LangGraph State Machine for Autonomous Revenue Recovery.

Implements the multi-step recovery lifecycle:
Intake -> Diagnose -> Policy Decision -> Confidence Gate -> Human Approval (Interrupt) -> Plan & Generate -> Dispatch -> Audit.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from src.agent.state import RecoveryState
from src.agent.tools import RazorpayTools, EvidenceBundler
from src.agent.payment_plans import PaymentPlanEngine
from src.agent.channels import ChannelDispatcher
from src.agent.checkpointer import get_checkpointer
from src.engine.risk_scorer import RiskScorer
from src.engine.policy import PolicyEngine
from src.engine.confidence_gate import ConfidenceGate
from src.engine.recovery_predictor import RecoveryPredictor
from src.llm.tone import ToneEngine
from src.llm.generators import MessageGenerator
from src.models.db_models import RelationshipTier, CommunicationChannel, ToneType
from src.observability.langfuse import observe_agent
from src.observability.metrics import record_invoice_processed, record_outreach_dispatched


# ---------------- Node Implementations ---------------- #

@observe_agent(name="intake_and_diagnose")
async def intake_and_diagnose_node(state: RecoveryState) -> Dict[str, Any]:
    """Diagnoses receivable health, computes risk score and recovery probability."""
    tier = RelationshipTier(state.get("relationship_tier", "STANDARD"))
    amount_paise = state["amount_paise"]
    days_overdue = state["days_overdue"]

    # 1. Calculate Risk Score
    risk_score, risk_band, _ = RiskScorer.calculate_risk(
        amount_paise=amount_paise,
        days_overdue=days_overdue,
        days_since_last_contact=3,
        broken_promises_count=1 if state.get("has_broken_promise") else 0,
        active_promises_count=1 if state.get("has_active_promise") else 0,
        credit_score=state.get("credit_score", 700),
        historical_recovery_rate=state.get("historical_recovery_rate", 0.85),
        relationship_tier=tier,
    )

    # 2. Predict Recovery Probability
    prediction = RecoveryPredictor.predict(
        amount_paise=amount_paise,
        days_overdue=days_overdue,
        days_since_last_contact=3,
        broken_promises_count=1 if state.get("has_broken_promise") else 0,
        historical_recovery_rate=state.get("historical_recovery_rate", 0.85),
        credit_score=state.get("credit_score", 700),
        relationship_tier=tier,
    )

    audit_entry = {
        "event_type": "DIAGNOSED",
        "actor": "AGENT",
        "action": f"Receivable diagnosed: Risk Score {risk_score} ({risk_band}), P(Recovery) = {prediction.recovery_probability:.1%}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "risk_score": risk_score,
        "risk_band": risk_band,
        "recovery_probability": prediction.recovery_probability,
        "current_stage": "DIAGNOSE",
        "audit_trail": [audit_entry],
    }


@observe_agent(name="policy_evaluation")
async def policy_evaluation_node(state: RecoveryState) -> Dict[str, Any]:
    """Evaluates deterministic policy rules to determine the next intervention."""
    tier = RelationshipTier(state.get("relationship_tier", "STANDARD"))
    current_level = state.get("current_level", 1)

    policy_decision = PolicyEngine.evaluate_next_action(
        current_level=current_level,
        days_overdue=state["days_overdue"],
        last_contact_time=None,  # First intervention in cycle
        has_active_promise=state.get("has_active_promise", False),
        has_broken_promise=state.get("has_broken_promise", False),
        is_disputed=state.get("is_disputed", False),
        amount_paise=state["amount_paise"],
        relationship_tier=tier,
    )

    audit_entry = {
        "event_type": "POLICY_EVALUATED",
        "actor": "POLICY_ENGINE",
        "action": (
            f"Next level: {policy_decision.next_level} via {policy_decision.channel.value}. "
            f"Action allowed: {policy_decision.should_act}. Rationale: {policy_decision.reason}"
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "current_level": policy_decision.next_level,
        "selected_channel": policy_decision.channel.value,
        "selected_tone": policy_decision.tone.value,
        "should_act": policy_decision.should_act,
        "requires_human_approval": policy_decision.requires_human_approval,
        "policy_reason": policy_decision.reason,
        "audit_trail": [audit_entry],
    }


async def confidence_check_node(state: RecoveryState) -> Dict[str, Any]:
    """Applies Feature 7 Confidence Gating to ensure safety before action."""
    confidence = state.get("confidence_score", 0.95)
    amount_paise = state["amount_paise"]

    gate_result = ConfidenceGate.evaluate(
        task="intent_classification",
        confidence=confidence,
        invoice_amount_paise=amount_paise,
    )

    requires_approval = state.get("requires_human_approval", False) or not gate_result.passed
    approval_reason = state.get("policy_reason", "")
    if not gate_result.passed:
        approval_reason = f"Confidence Gating Triggered: {gate_result.reason}"

    audit_entry = {
        "event_type": "CONFIDENCE_GATED",
        "actor": "CONFIDENCE_GATE",
        "action": f"Gate result: {'PASSED' if gate_result.passed else 'HELD_FOR_HUMAN'}. Confidence: {confidence:.1%}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "confidence_gate_passed": gate_result.passed,
        "requires_human_approval": requires_approval,
        "approval_reason": approval_reason,
        "approval_type": "CONFIDENCE_ESCALATION" if not gate_result.passed else "LEGAL_NOTICE",
        "audit_trail": [audit_entry],
    }


async def human_approval_gate_node(state: RecoveryState) -> Dict[str, Any]:
    """Human-in-the-loop checkpoint. In LangGraph, execution pauses before this node."""
    approved = state.get("human_approved", True)
    audit_entry = {
        "event_type": "HUMAN_REVIEW_RESOLVED",
        "actor": "HUMAN_SUPERVISOR",
        "action": f"Intervention {'APPROVED' if approved else 'REJECTED'} by supervisor.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return {
        "human_approved": approved,
        "audit_trail": [audit_entry],
    }


async def plan_and_generate_node(state: RecoveryState) -> Dict[str, Any]:
    """Generates tone-adjusted communication copy and generates Razorpay payment link."""
    tier = RelationshipTier(state.get("relationship_tier", "STANDARD"))
    target_channel = CommunicationChannel(state["selected_channel"])
    tone_type = ToneType(state["selected_tone"])
    amount_paise = state["amount_paise"]

    # 1. Create or retrieve Razorpay Payment Link
    link_data = await RazorpayTools.create_payment_link(
        amount_paise=amount_paise,
        invoice_number=state["invoice_number"],
        customer_name=state["customer_name"],
        customer_email=state["customer_email"],
        customer_phone=state.get("customer_phone"),
        reference_id=state["invoice_id"],
        description=f"Payment for invoice {state['invoice_number']}",
    )

    # 2. Evaluate Payment Plan offer if level >= 3
    payment_plan = None
    if state["current_level"] >= 3:
        payment_plan = PaymentPlanEngine.generate_plan(
            amount_paise=amount_paise,
            relationship_tier=tier,
            broken_promises_count=1 if state.get("has_broken_promise") else 0,
        )

    # 3. Dynamic Message Generation
    content, subject = MessageGenerator.generate_message(
        channel=target_channel,
        tone=tone_type,
        customer_name=state["customer_name"],
        invoice_number=state["invoice_number"],
        amount_paise=amount_paise,
        days_overdue=state["days_overdue"],
        payment_link_url=link_data["payment_link_url"],
        due_date_str=state.get("due_date_str", "recent"),
    )

    audit_entry = {
        "event_type": "ACTION_PLANNED",
        "actor": "AGENT",
        "action": f"Generated {target_channel.value} message with {tone_type.value} tone. Payment Link: {link_data['payment_link_id']}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "payment_link_id": link_data["payment_link_id"],
        "payment_link_url": link_data["payment_link_url"],
        "payment_plan_offered": bool(payment_plan),
        "payment_plan_details": payment_plan,
        "last_message_content": content,
        "last_message_subject": subject,
        "audit_trail": [audit_entry],
    }


@observe_agent(name="dispatch_action")
async def dispatch_action_node(state: RecoveryState) -> Dict[str, Any]:
    """Dispatches communication via Multi-Channel Dispatcher."""
    target_channel = CommunicationChannel(state["selected_channel"])
    recipient = state.get("customer_phone") if target_channel in (CommunicationChannel.WHATSAPP, CommunicationChannel.SMS) else state["customer_email"]

    resolved_channel, fallback_note = ChannelDispatcher.resolve_channel(
        target_channel=target_channel,
        has_email=bool(state.get("customer_email")),
        has_phone=bool(state.get("customer_phone")),
    )

    dispatch_result = ChannelDispatcher.simulate_dispatch(
        channel=resolved_channel,
        recipient=recipient or state["customer_email"],
        content=state["last_message_content"],
        subject=state.get("last_message_subject"),
    )

    try:
        record_outreach_dispatched(resolved_channel.value, dispatch_result["delivery_status"])
    except Exception:
        pass

    audit_actions = [f"Dispatched message via {resolved_channel.value} to {recipient}"]
    if fallback_note:
        audit_actions.append(fallback_note)

    audit_entry = {
        "event_type": "COMMUNICATION_DISPATCHED",
        "actor": "CHANNEL_DISPATCHER",
        "action": " | ".join(audit_actions),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    message_record = {
        "channel": resolved_channel.value,
        "recipient": recipient,
        "content": state["last_message_content"],
        "subject": state.get("last_message_subject"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "delivery_status": dispatch_result["delivery_status"],
    }

    return {
        "current_stage": "ACT",
        "messages": [message_record],
        "audit_trail": [audit_entry],
    }


# ---------------- Conditional Routing Logic ---------------- #

def route_after_policy(state: RecoveryState) -> Literal["confidence_check", "end"]:
    if not state.get("should_act", True):
        return "end"
    return "confidence_check"


def route_after_confidence(state: RecoveryState) -> Literal["human_approval_gate", "plan_and_generate"]:
    if state.get("requires_human_approval", False):
        return "human_approval_gate"
    return "plan_and_generate"


def route_after_human_approval(state: RecoveryState) -> Literal["plan_and_generate", "end"]:
    if state.get("human_approved", False):
        return "plan_and_generate"
    return "end"


# ---------------- Graph Construction ---------------- #

def build_recovery_graph(interrupt_human: bool = False, checkpointer: Any = None):
    """Builds and compiles the LangGraph state machine with optional human interruption and checkpointing."""
    workflow = StateGraph(RecoveryState)

    # Add Nodes
    workflow.add_node("intake_and_diagnose", intake_and_diagnose_node)
    workflow.add_node("policy_evaluation", policy_evaluation_node)
    workflow.add_node("confidence_check", confidence_check_node)
    workflow.add_node("human_approval_gate", human_approval_gate_node)
    workflow.add_node("plan_and_generate", plan_and_generate_node)
    workflow.add_node("dispatch_action", dispatch_action_node)

    # Add Edges
    workflow.set_entry_point("intake_and_diagnose")
    workflow.add_edge("intake_and_diagnose", "policy_evaluation")

    workflow.add_conditional_edges(
        "policy_evaluation",
        route_after_policy,
        {
            "confidence_check": "confidence_check",
            "end": END,
        }
    )

    workflow.add_conditional_edges(
        "confidence_check",
        route_after_confidence,
        {
            "human_approval_gate": "human_approval_gate",
            "plan_and_generate": "plan_and_generate",
        }
    )

    workflow.add_conditional_edges(
        "human_approval_gate",
        route_after_human_approval,
        {
            "plan_and_generate": "plan_and_generate",
            "end": END,
        }
    )

    workflow.add_edge("plan_and_generate", "dispatch_action")
    workflow.add_edge("dispatch_action", END)

    if interrupt_human:
        cp = checkpointer or get_checkpointer()
        return workflow.compile(checkpointer=cp, interrupt_before=["human_approval_gate"])
    if checkpointer is not None:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()


# Default singleton instance for production with human interruption enabled
recovery_agent = build_recovery_graph(interrupt_human=True)

