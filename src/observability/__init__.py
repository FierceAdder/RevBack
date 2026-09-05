"""Observability module for RevBack.
Provides Langfuse LLM tracing and Prometheus system/business metrics.
"""

from src.observability.langfuse import get_langfuse_client, setup_langfuse, observe_agent
from src.observability.metrics import (
    INVOICE_PROCESSED_TOTAL,
    REVENUE_RECOVERED_PAISE,
    AGENT_RUN_DURATION_SECONDS,
    HUMAN_APPROVALS_TOTAL,
    LLM_TOKEN_USAGE_TOTAL,
    OUTREACH_DISPATCHED_TOTAL,
    record_invoice_processed,
    record_revenue_recovered,
    record_llm_tokens,
    get_prometheus_metrics,
)

__all__ = [
    "get_langfuse_client",
    "setup_langfuse",
    "observe_agent",
    "INVOICE_PROCESSED_TOTAL",
    "REVENUE_RECOVERED_PAISE",
    "AGENT_RUN_DURATION_SECONDS",
    "HUMAN_APPROVALS_TOTAL",
    "LLM_TOKEN_USAGE_TOTAL",
    "OUTREACH_DISPATCHED_TOTAL",
    "record_invoice_processed",
    "record_revenue_recovered",
    "record_llm_tokens",
    "get_prometheus_metrics",
]
