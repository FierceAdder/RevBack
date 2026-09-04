"""Unit tests for DebtorExtractors (Promise extraction, Intent classification, Dispute detection)."""

import pytest
from src.llm.extractors import DebtorExtractors


@pytest.mark.asyncio
async def test_extract_valid_promise():
    """Debtor message clearly stating payment commitment is extracted with high confidence."""
    text = "We will transfer ₹1,50,000 by this Friday. Please hold off on any escalation."
    result = await DebtorExtractors.extract_promise(text, invoice_amount_paise=150_000_00)

    assert result.has_promise is True
    assert result.promised_amount_paise == 150_000_00
    assert result.promise_date_iso is not None
    assert result.confidence >= 0.85
    assert result.raw_quote is not None


@pytest.mark.asyncio
async def test_extract_ambiguous_promise_low_confidence():
    """Ambiguous promise yields low confidence, suitable for confidence gating."""
    text = "We might try to pay something next week if our clients clear their bills."
    result = await DebtorExtractors.extract_promise(text, invoice_amount_paise=200_000_00)

    assert result.has_promise is True
    assert result.confidence < 0.80  # Low confidence will fail ConfidenceGate and route to human!


@pytest.mark.asyncio
async def test_classify_dispute_intent():
    """Dispute classification identifies dispute intent and triggers dispute categorization."""
    text = "This invoice is wrong! You billed us for 50 licenses but we only ordered 25. We dispute this amount."
    intent_res = await DebtorExtractors.classify_intent(text)
    assert intent_res.intent == "DISPUTE"
    assert intent_res.confidence >= 0.90

    dispute_res = await DebtorExtractors.extract_dispute(text)
    assert dispute_res.is_disputed is True
    assert dispute_res.dispute_category == "BILLING_ERROR"


@pytest.mark.asyncio
async def test_classify_already_paid_intent():
    """Already paid intent detection."""
    text = "Payment was already completed yesterday via NEFT. UTR number is CMS2938482928. Check your bank statement."
    intent_res = await DebtorExtractors.classify_intent(text)
    assert intent_res.intent == "ALREADY_PAID"
    assert intent_res.confidence >= 0.90
