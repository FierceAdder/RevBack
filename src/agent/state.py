"""LangGraph Agent State Definitions.

Defines the complete typed state representing an invoice undergoing recovery,
including financial exposure, risk metrics, communication history, and audit trail.
"""

from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
import operator


class RecoveryState(TypedDict):
    """The central state of the LangGraph recovery workflow."""

    # Core Identifiers & Financials
    invoice_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    invoice_number: str
    amount_paise: int
    amount_paid_paise: int
    due_date_str: str
    days_overdue: int

    # Customer Attributes
    relationship_tier: str
    credit_score: int
    historical_recovery_rate: float

    # Lifecycle State
    current_stage: str
    current_level: int
    is_recovered: bool
    is_disputed: bool
    dispute_reason: Optional[str]

    # Deterministic Engine Outputs
    risk_score: float
    risk_band: str
    recovery_probability: float
    selected_channel: str
    selected_tone: str
    should_act: bool
    policy_reason: str

    # Promises & Payment Plans
    has_active_promise: bool
    has_broken_promise: bool
    active_promise_amount_paise: Optional[int]
    active_promise_date_str: Optional[str]
    payment_plan_offered: bool
    payment_plan_details: Optional[Dict[str, Any]]

    # Razorpay Details
    payment_link_id: Optional[str]
    payment_link_url: Optional[str]

    # Human-in-the-Loop & Confidence Gating
    confidence_score: float
    confidence_gate_passed: bool
    requires_human_approval: bool
    human_approved: Optional[bool]
    approval_type: Optional[str]
    approval_reason: Optional[str]

    # Multi-turn History & Auditing (Appended monotonically)
    last_message_content: Optional[str]
    last_message_subject: Optional[str]
    messages: Annotated[List[Dict[str, Any]], operator.add]
    audit_trail: Annotated[List[Dict[str, Any]], operator.add]
