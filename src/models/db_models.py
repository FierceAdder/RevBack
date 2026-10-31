"""SQLAlchemy database models with bitemporal timestamps and foreign key relationships."""

from datetime import datetime, timezone
import enum
from typing import Optional, List
import uuid

from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class InvoiceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    DISPUTED = "DISPUTED"
    CANCELLED = "CANCELLED"
    WRITTEN_OFF = "WRITTEN_OFF"


class RecoveryStage(str, enum.Enum):
    INTAKE = "INTAKE"
    DIAGNOSE = "DIAGNOSE"
    ACT = "ACT"
    PROMISE_TRACKING = "PROMISE_TRACKING"
    ESCALATION = "ESCALATION"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"


class RelationshipTier(str, enum.Enum):
    ENTERPRISE_VIP = "ENTERPRISE_VIP"
    KEY_ACCOUNT = "KEY_ACCOUNT"
    STANDARD = "STANDARD"
    HIGH_RISK = "HIGH_RISK"


class CommunicationChannel(str, enum.Enum):
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    FORMAL_NOTICE = "FORMAL_NOTICE"
    PHONE = "PHONE"


class CommunicationDirection(str, enum.Enum):
    OUTBOUND = "OUTBOUND"
    INBOUND = "INBOUND"


class CommunicationStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    REPLIED = "REPLIED"
    FAILED = "FAILED"


class ToneType(str, enum.Enum):
    COLLABORATIVE = "COLLABORATIVE"
    PROFESSIONAL = "PROFESSIONAL"
    FIRM = "FIRM"
    URGENT = "URGENT"
    FORMAL_LEGAL = "FORMAL_LEGAL"


class PromiseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    KEPT = "KEPT"
    BROKEN = "BROKEN"
    RENEGOTIATED = "RENEGOTIATED"


class PlanStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    DEFAULTED = "DEFAULTED"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class ApprovalType(str, enum.Enum):
    LEGAL_NOTICE = "LEGAL_NOTICE"
    SETTLEMENT_DISCOUNT = "SETTLEMENT_DISCOUNT"
    WRITE_OFF = "WRITE_OFF"
    CONFIDENCE_ESCALATION = "CONFIDENCE_ESCALATION"


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    VIEWER = "VIEWER"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    razorpay_key_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    razorpay_key_secret: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    razorpay_account_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    settings_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    users: Mapped[List["User"]] = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    api_keys: Mapped[List["ApiKey"]] = relationship("ApiKey", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.ADMIN)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant", back_populates="users", lazy="selectin")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), default="ADMIN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="api_keys")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    razorpay_customer_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    business_type: Mapped[str] = mapped_column(String(64), default="B2B_SAAS")
    relationship_tier: Mapped[RelationshipTier] = mapped_column(
        SQLEnum(RelationshipTier), default=RelationshipTier.STANDARD
    )
    credit_score: Mapped[int] = mapped_column(Integer, default=700)
    total_invoiced_paise: Mapped[int] = mapped_column(Integer, default=0)
    total_recovered_paise: Mapped[int] = mapped_column(Integer, default=0)
    historical_recovery_rate: Mapped[float] = mapped_column(Float, default=0.85)
    preferred_channel: Mapped[CommunicationChannel] = mapped_column(
        SQLEnum(CommunicationChannel), default=CommunicationChannel.EMAIL
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="customer")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    agent_thread_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    razorpay_invoice_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paid_paise: Mapped[int] = mapped_column(Integer, default=0)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus), default=InvoiceStatus.PENDING, index=True)
    current_stage: Mapped[RecoveryStage] = mapped_column(SQLEnum(RecoveryStage), default=RecoveryStage.INTAKE, index=True)
    current_level: Mapped[int] = mapped_column(Integer, default=1)  # Levels 1 to 7
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0 to 100
    recovery_probability: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 to 1.0 (Feature 2)
    optimal_tone: Mapped[ToneType] = mapped_column(SQLEnum(ToneType), default=ToneType.COLLABORATIVE)  # Feature 1
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)  # Feature 7
    active_razorpay_payment_link_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    active_payment_link_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    dispute_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Bitemporal tracking
    valid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="invoices")
    promises: Mapped[List["Promise"]] = relationship("Promise", back_populates="invoice", cascade="all, delete-orphan")
    payment_plans: Mapped[List["PaymentPlan"]] = relationship("PaymentPlan", back_populates="invoice", cascade="all, delete-orphan")
    communications: Mapped[List["Communication"]] = relationship("Communication", back_populates="invoice", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="invoice", cascade="all, delete-orphan")
    approvals: Mapped[List["HumanApproval"]] = relationship("HumanApproval", back_populates="invoice", cascade="all, delete-orphan")


class Promise(Base):
    __tablename__ = "promises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False, index=True)
    promised_amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    promise_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[PromiseStatus] = mapped_column(SQLEnum(PromiseStatus), default=PromiseStatus.ACTIVE, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    raw_quote: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_from_comm_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Bitemporal tracking
    valid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="promises")


class PaymentPlan(Base):
    __tablename__ = "payment_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False, index=True)
    total_amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    installment_count: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency_days: Mapped[int] = mapped_column(Integer, default=14)
    status: Mapped[PlanStatus] = mapped_column(SQLEnum(PlanStatus), default=PlanStatus.PROPOSED)
    terms_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Bitemporal tracking
    valid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payment_plans")
    installments: Mapped[List["PaymentPlanInstallment"]] = relationship(
        "PaymentPlanInstallment", back_populates="payment_plan", cascade="all, delete-orphan"
    )


class PaymentPlanInstallment(Base):
    __tablename__ = "payment_plan_installments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    payment_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("payment_plans.id"), nullable=False, index=True)
    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    razorpay_payment_link_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    payment_plan: Mapped["PaymentPlan"] = relationship("PaymentPlan", back_populates="installments")


class Communication(Base):
    __tablename__ = "communications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False, index=True)
    channel: Mapped[CommunicationChannel] = mapped_column(SQLEnum(CommunicationChannel), nullable=False)
    direction: Mapped[CommunicationDirection] = mapped_column(SQLEnum(CommunicationDirection), default=CommunicationDirection.OUTBOUND)
    sender: Mapped[str] = mapped_column(String(255), default="RevBack Agent")
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intervention_level: Mapped[int] = mapped_column(Integer, default=1)
    tone: Mapped[ToneType] = mapped_column(SQLEnum(ToneType), default=ToneType.COLLABORATIVE)
    status: Mapped[CommunicationStatus] = mapped_column(SQLEnum(CommunicationStatus), default=CommunicationStatus.SENT)
    scheduled_send_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Bitemporal tracking
    valid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="communications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(64), default="AGENT")
    action: Mapped[str] = mapped_column(Text, nullable=False)
    previous_state: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    new_state: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    token_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="audit_logs")


class ProcessedPayment(Base):
    """One row per Razorpay payment already applied to an invoice.

    Razorpay delivers webhooks at least once, and a payment-link payment also arrives
    as both payment.captured and payment_link.paid. The primary key makes applying the
    same payment twice impossible, even when deliveries race.
    """
    __tablename__ = "processed_payments"

    payment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False, index=True)
    event: Mapped[str] = mapped_column(String(64), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class HumanApproval(Base):
    __tablename__ = "human_approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False, index=True)
    action_type: Mapped[ApprovalType] = mapped_column(SQLEnum(ApprovalType), nullable=False)
    proposed_action_details: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="approvals")
