"""Prometheus runtime and business metrics for RevBack.
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

# Business Metrics
INVOICE_PROCESSED_TOTAL = Counter(
    "revback_invoices_processed_total",
    "Total invoices processed by the recovery agent",
    ["status", "stage"],
)

REVENUE_RECOVERED_PAISE = Counter(
    "revback_revenue_recovered_paise_total",
    "Total revenue successfully recovered in paise",
    ["channel"],
)

OUTREACH_DISPATCHED_TOTAL = Counter(
    "revback_outreach_dispatched_total",
    "Outreach notifications and messages dispatched",
    ["channel", "status"],
)

HUMAN_APPROVALS_TOTAL = Counter(
    "revback_human_approvals_total",
    "Human approval decisions taken by supervisors",
    ["decision"],
)

ACTIVE_COLLECTIONS_GAUGE = Gauge(
    "revback_active_collections_count",
    "Count of currently outstanding or delinquent invoices being tracked",
)

# LLM & System Performance Metrics
AGENT_RUN_DURATION_SECONDS = Histogram(
    "revback_agent_run_duration_seconds",
    "Execution duration for the LangGraph recovery agent in seconds",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

LLM_TOKEN_USAGE_TOTAL = Counter(
    "revback_llm_tokens_total",
    "Cumulative LLM tokens consumed by the recovery system",
    ["model", "token_type"],
)


def record_invoice_processed(status: str, stage: str) -> None:
    """Record an invoice processing event."""
    try:
        INVOICE_PROCESSED_TOTAL.labels(status=status, stage=stage).inc()
    except Exception:
        pass


def record_revenue_recovered(amount_paise: int, channel: str = "RAZORPAY_PAYMENT_LINK") -> None:
    """Record recovered revenue in paise."""
    try:
        REVENUE_RECOVERED_PAISE.labels(channel=channel).inc(amount_paise)
    except Exception:
        pass


def record_outreach_dispatched(channel: str, status: str = "SUCCESS") -> None:
    """Record outbound message dispatch."""
    try:
        OUTREACH_DISPATCHED_TOTAL.labels(channel=channel, status=status).inc()
    except Exception:
        pass


def record_human_approval(decision: str) -> None:
    """Record a human supervisor approval or rejection."""
    try:
        HUMAN_APPROVALS_TOTAL.labels(decision=decision).inc()
    except Exception:
        pass


def record_llm_tokens(model: str, prompt_tokens: int, completion_tokens: int) -> None:
    """Record token consumption for prompt and completion."""
    try:
        if prompt_tokens > 0:
            LLM_TOKEN_USAGE_TOTAL.labels(model=model, token_type="prompt").inc(prompt_tokens)
        if completion_tokens > 0:
            LLM_TOKEN_USAGE_TOTAL.labels(model=model, token_type="completion").inc(completion_tokens)
    except Exception:
        pass


def get_prometheus_metrics() -> bytes:
    """Generate the latest Prometheus exposition format text."""
    return generate_latest(REGISTRY)
