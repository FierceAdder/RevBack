"""Pydantic v2 domain schemas and API contracts."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from src.models.db_models import (
    InvoiceStatus, RecoveryStage, RelationshipTier,
    CommunicationChannel, CommunicationDirection, CommunicationStatus,
    ToneType, PromiseStatus, PlanStatus, ApprovalStatus, ApprovalType
)


# ---------------- Customer Schemas ---------------- #

class CustomerBase(BaseModel):
    name: str = Field(..., description="Company or customer business name")
    email: str = Field(..., description="Primary contact email")
    phone: Optional[str] = None
    business_type: str = "B2B_SAAS"
    relationship_tier: RelationshipTier = RelationshipTier.STANDARD
    credit_score: int = Field(default=700, ge=300, le=900)
    preferred_channel: CommunicationChannel = CommunicationChannel.EMAIL


class CustomerCreate(CustomerBase):
    razorpay_customer_id: Optional[str] = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    razorpay_customer_id: Optional[str] = None
    total_invoiced_paise: int
    total_recovered_paise: int
    historical_recovery_rate: float
    created_at: datetime
    updated_at: datetime


# ---------------- Promise Schemas ---------------- #

class PromiseBase(BaseModel):
    promised_amount_paise: int
    promise_date: datetime
    status: PromiseStatus = PromiseStatus.ACTIVE
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    raw_quote: Optional[str] = None


class PromiseCreate(PromiseBase):
    invoice_id: str
    extracted_from_comm_id: Optional[str] = None


class PromiseRead(PromiseBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    extracted_from_comm_id: Optional[str] = None
    valid_at: datetime
    recorded_at: datetime
    created_at: datetime


# ---------------- Payment Plan Schemas ---------------- #

class InstallmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    installment_number: int
    amount_paise: int
    due_date: datetime
    razorpay_payment_link_id: Optional[str] = None
    status: str
    paid_at: Optional[datetime] = None


class PaymentPlanCreate(BaseModel):
    invoice_id: str
    installment_count: int = Field(default=3, ge=2, le=6)
    frequency_days: int = Field(default=14, ge=7, le=30)
    terms_summary: str


class PaymentPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    total_amount_paise: int
    installment_count: int
    frequency_days: int
    status: PlanStatus
    terms_summary: str
    valid_at: datetime
    recorded_at: datetime
    created_at: datetime
    installments: List[InstallmentRead] = []


# ---------------- Communication Schemas ---------------- #

class CommunicationCreate(BaseModel):
    invoice_id: str
    channel: CommunicationChannel
    direction: CommunicationDirection = CommunicationDirection.OUTBOUND
    sender: str = "RevBack Agent"
    recipient: str
    subject: Optional[str] = None
    content: str
    intervention_level: int = 1
    tone: ToneType = ToneType.COLLABORATIVE
    status: CommunicationStatus = CommunicationStatus.SENT
    scheduled_send_time: Optional[datetime] = None


class CommunicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    channel: CommunicationChannel
    direction: CommunicationDirection
    sender: str
    recipient: str
    subject: Optional[str] = None
    content: str
    intervention_level: int
    tone: ToneType
    status: CommunicationStatus
    scheduled_send_time: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    valid_at: datetime
    recorded_at: datetime
    created_at: datetime


# ---------------- Audit Log Schemas ---------------- #

class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    event_type: str
    actor: str
    action: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    reasoning: Optional[str] = None
    confidence_score: Optional[float] = None
    token_cost_usd: float = 0.0
    metadata_json: Optional[Dict[str, Any]] = None
    recorded_at: datetime


# ---------------- Human Approval Schemas ---------------- #

class HumanApprovalCreate(BaseModel):
    invoice_id: str
    action_type: ApprovalType
    proposed_action_details: Dict[str, Any]
    confidence: float
    threshold: float


class HumanApprovalAction(BaseModel):
    status: ApprovalStatus  # APPROVED, REJECTED, MODIFIED
    reviewer_id: str
    review_notes: Optional[str] = None
    modified_details: Optional[Dict[str, Any]] = None


class HumanApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    action_type: ApprovalType
    proposed_action_details: Dict[str, Any]
    confidence: float
    threshold: float
    status: ApprovalStatus
    reviewer_id: Optional[str] = None
    review_notes: Optional[str] = None
    requested_at: datetime
    resolved_at: Optional[datetime] = None


# ---------------- Invoice Schemas ---------------- #

class InvoiceBase(BaseModel):
    invoice_number: str
    amount_paise: int = Field(..., gt=0)
    due_date: datetime


class InvoiceCreate(InvoiceBase):
    customer_id: str
    razorpay_invoice_id: Optional[str] = None


class InvoiceRead(InvoiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    razorpay_invoice_id: Optional[str] = None
    customer_id: str
    amount_paid_paise: int
    status: InvoiceStatus
    current_stage: RecoveryStage
    current_level: int
    risk_score: float
    recovery_probability: float
    optimal_tone: ToneType
    confidence_score: float
    active_razorpay_payment_link_id: Optional[str] = None
    active_payment_link_url: Optional[str] = None
    dispute_reason: Optional[str] = None
    valid_at: datetime
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime
    customer: Optional[CustomerRead] = None


class InvoiceDetailRead(InvoiceRead):
    promises: List[PromiseRead] = []
    payment_plans: List[PaymentPlanRead] = []
    communications: List[CommunicationRead] = []
    audit_logs: List[AuditLogRead] = []
    approvals: List[HumanApprovalRead] = []


# ---------------- Engine & Decision Schemas ---------------- #

class GateResult(BaseModel):
    passed: bool
    action: str  # "proceed" | "route_to_human"
    task: str
    confidence: float
    threshold: float
    reason: Optional[str] = None
    invoice_amount: int


class RecoveryPrediction(BaseModel):
    recovery_probability: float = Field(..., ge=0.0, le=1.0)
    risk_band: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    recommended_path: str
    factors: Dict[str, float]
    suggested_level: int
    suggested_tone: ToneType


class ToneAnalysis(BaseModel):
    persona: str
    recommended_tone: ToneType
    rationale: str
    formality_level: int = Field(ge=1, le=5)


# ---------------- Simulation & Evaluation Schemas ---------------- #

class SimulationRunRequest(BaseModel):
    invoice_count: int = Field(default=50, ge=10, le=500)
    include_baseline: bool = True
    random_seed: Optional[int] = 42


class StrategyMetrics(BaseModel):
    strategy_name: str
    total_invoices: int
    total_at_risk_paise: int
    total_recovered_paise: int
    recovery_rate_pct: float
    average_days_to_recovery: float
    cost_spent_usd: float
    net_recovery_paise: int
    broken_promises_count: int
    legal_escalations_count: int


class SimulationComparisonResult(BaseModel):
    baseline: StrategyMetrics
    agent: StrategyMetrics
    uplift_percentage_points: float
    dso_reduction_days: float
    roi_multiple: float
    cost_per_recovery_paise: float
    run_timestamp: datetime
