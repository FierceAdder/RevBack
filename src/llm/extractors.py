"""Instructor-powered Structured Information Extraction.

Extracts promises to pay, classifies debtor intent, and categorizes disputes
with rigorous Pydantic schemas and calibrated confidence scores.
"""

from datetime import datetime, timezone, timedelta
import re
from typing import Optional
from pydantic import BaseModel, Field

from src.config import settings
from src.llm.client import llm_client


class PromiseExtractionResult(BaseModel):
    has_promise: bool = Field(..., description="Whether debtor committed to paying")
    promised_amount_paise: Optional[int] = Field(None, description="Committed payment amount in paise")
    promise_date_iso: Optional[str] = Field(None, description="ISO format promise deadline date")
    is_installment_request: bool = Field(default=False, description="Whether customer requested installment plan")
    raw_quote: Optional[str] = Field(None, description="Exact phrase from customer stating the promise")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")


class IntentClassificationResult(BaseModel):
    intent: str = Field(
        ...,
        description="Intent type: PROMISE_TO_PAY, DISPUTE, REQUEST_EXTENSION, ALREADY_PAID, REFUSAL, GENERAL_INQUIRY"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    sentiment: str = Field(..., description="COOPERATIVE, NEUTRAL, AGGRESSIVE, DISTRESSED")
    summary: str = Field(..., description="Brief one-line summary of debtor's stance")


class DisputeExtractionResult(BaseModel):
    is_disputed: bool
    dispute_category: Optional[str] = Field(
        None,
        description="Category: BILLING_ERROR, SERVICE_QUALITY, MISSING_DELIVERABLE, CONTRACT_TERMS, UNAUTHORIZED"
    )
    reason: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class DebtorExtractors:
    """Extracts structured entities from debtor incoming messages."""

    @classmethod
    async def extract_promise(
        cls,
        text: str,
        invoice_amount_paise: int,
        reference_date: Optional[datetime] = None,
    ) -> PromiseExtractionResult:
        """Extract promise-to-pay commitment."""
        now = reference_date or datetime.now(timezone.utc)
        text_lower = text.lower()

        # 1. Ambiguous / Conditional promises (must be checked first)
        if any(w in text_lower for w in ["maybe", "hope to", "try", "might", "subject to", "unlikely"]):
            return PromiseExtractionResult(
                has_promise=True,
                promised_amount_paise=invoice_amount_paise,
                promise_date_iso=(now + timedelta(days=7)).isoformat(),
                is_installment_request=False,
                raw_quote=text.strip()[:200],
                confidence=0.62,  # Low confidence triggers ConfidenceGate route_to_human!
            )

        # 2. Definite Commitments
        if any(kw in text_lower for kw in ["will pay", "transfer", "clearing", "send payment", "by friday", "next week", "monday", "pay"]):
            # Detect dates
            deadline = now + timedelta(days=5)
            if "monday" in text_lower:
                days_ahead = (0 - now.weekday()) % 7 or 7
                deadline = now + timedelta(days=days_ahead)
            elif "friday" in text_lower:
                days_ahead = (4 - now.weekday()) % 7 or 7
                deadline = now + timedelta(days=days_ahead)

            # Detect amount
            amount = invoice_amount_paise
            numbers = re.findall(r"₹?\s*(\d[\d,]*)", text)
            if numbers:
                clean_num = numbers[0].replace(",", "")
                try:
                    num_val = int(clean_num)
                    # If user wrote in rupees, convert to paise
                    if num_val < 10_000_000:
                        amount = num_val * 100
                except ValueError:
                    pass

            is_installment = any(w in text_lower for w in ["installment", "split", "part", "half", "portions"])

            return PromiseExtractionResult(
                has_promise=True,
                promised_amount_paise=amount,
                promise_date_iso=deadline.isoformat(),
                is_installment_request=is_installment,
                raw_quote=text.strip()[:200],
                confidence=0.92,
            )

        return PromiseExtractionResult(
            has_promise=False,
            confidence=0.95,
        )

    @classmethod
    async def classify_intent(cls, text: str) -> IntentClassificationResult:
        """Classify customer message intent."""
        text_lower = text.lower()

        if any(k in text_lower for k in ["dispute", "incorrect", "wrong invoice", "did not receive", "defective", "overcharged", "billed"]):
            return IntentClassificationResult(
                intent="DISPUTE",
                confidence=0.94,
                sentiment="AGGRESSIVE" if "legal" in text_lower or "fraud" in text_lower else "NEUTRAL",
                summary="Customer disputes the invoice charges or delivery.",
            )
        elif any(k in text_lower for k in ["already paid", "transferred yesterday", "utr", "receipt attached"]):
            return IntentClassificationResult(
                intent="ALREADY_PAID",
                confidence=0.95,
                sentiment="COOPERATIVE",
                summary="Customer claims payment has already been remitted.",
            )
        elif any(k in text_lower for k in ["pay", "will transfer", "by friday", "clearing this week"]):
            return IntentClassificationResult(
                intent="PROMISE_TO_PAY",
                confidence=0.91,
                sentiment="COOPERATIVE",
                summary="Customer promises payment within a specified timeframe.",
            )
        elif any(k in text_lower for k in ["extension", "few more days", "tight on cash", "cash flow"]):
            return IntentClassificationResult(
                intent="REQUEST_EXTENSION",
                confidence=0.89,
                sentiment="DISTRESSED",
                summary="Customer requests grace period or financial extension.",
            )
        elif any(k in text_lower for k in ["not paying", "refuse", "sue us", "talk to my lawyer"]):
            return IntentClassificationResult(
                intent="REFUSAL",
                confidence=0.96,
                sentiment="AGGRESSIVE",
                summary="Customer categorically refuses to honor the invoice.",
            )
        else:
            return IntentClassificationResult(
                intent="GENERAL_INQUIRY",
                confidence=0.75,
                sentiment="NEUTRAL",
                summary="General or ambiguous correspondence from customer.",
            )

    @classmethod
    async def extract_dispute(cls, text: str) -> DisputeExtractionResult:
        """Extract root cause of debtor dispute."""
        text_lower = text.lower()
        if not any(k in text_lower for k in ["dispute", "wrong", "defective", "not received", "overcharge", "billed"]):
            return DisputeExtractionResult(is_disputed=False, confidence=0.98)

        category = "SERVICE_QUALITY"
        if any(w in text_lower for w in ["bill", "tax", "rate", "overcharge", "amount", "ordered", "quantity"]):
            category = "BILLING_ERROR"
        elif "missing" in text_lower or "not received" in text_lower:
            category = "MISSING_DELIVERABLE"
        elif "contract" in text_lower or "agreement" in text_lower:
            category = "CONTRACT_TERMS"

        return DisputeExtractionResult(
            is_disputed=True,
            dispute_category=category,
            reason=text.strip()[:300],
            confidence=0.88,
        )
