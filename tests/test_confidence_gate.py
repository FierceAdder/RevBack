"""Unit tests for ConfidenceGate (Feature 7)."""

from src.engine.confidence_gate import ConfidenceGate


def test_confidence_gate_passes_high_confidence():
    """High confidence extraction passes the gate without human intervention."""
    res = ConfidenceGate.evaluate(
        task="promise_extraction",
        confidence=0.92,
        invoice_amount_paise=150_000_00,  # ₹1.5 Lakhs
    )
    assert res.passed is True
    assert res.action == "proceed"


def test_confidence_gate_fails_low_confidence():
    """Uncertain extraction triggers route to human."""
    res = ConfidenceGate.evaluate(
        task="promise_extraction",
        confidence=0.68,  # Below 0.85 threshold
        invoice_amount_paise=150_000_00,
    )
    assert res.passed is False
    assert res.action == "route_to_human"
    assert "below" in res.reason.lower()


def test_dynamic_threshold_for_high_value_invoices():
    """Invoices > ₹5 Lakhs enforce stricter gating threshold (+5%)."""
    # 0.86 would pass standard threshold (0.85), but fails dynamic threshold (0.90) for ₹10 Lakhs
    res_standard = ConfidenceGate.evaluate(
        task="promise_extraction",
        confidence=0.86,
        invoice_amount_paise=200_000_00,  # ₹2 Lakhs
    )
    assert res_standard.passed is True

    res_large = ConfidenceGate.evaluate(
        task="promise_extraction",
        confidence=0.86,
        invoice_amount_paise=1000_000_00,  # ₹10 Lakhs
    )
    assert res_large.passed is False
    assert res_large.action == "route_to_human"
    assert res_large.threshold >= 0.90
