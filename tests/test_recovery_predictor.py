"""Unit tests for RecoveryPredictor (Feature 2)."""

from src.engine.recovery_predictor import RecoveryPredictor
from src.models.db_models import RelationshipTier, ToneType


def test_high_recovery_probability():
    """Customer with good history and only 5 days overdue has high probability."""
    pred = RecoveryPredictor.predict(
        amount_paise=100_000_00,
        days_overdue=5,
        days_since_last_contact=2,
        broken_promises_count=0,
        historical_recovery_rate=0.95,
        credit_score=780,
        relationship_tier=RelationshipTier.KEY_ACCOUNT,
    )
    assert pred.recovery_probability >= 0.75
    assert pred.risk_band in ("LOW", "MEDIUM")
    assert pred.suggested_tone in (ToneType.COLLABORATIVE, ToneType.PROFESSIONAL)


def test_low_recovery_probability_chronic_default():
    """Customer with broken promises and 60 days overdue has low probability."""
    pred = RecoveryPredictor.predict(
        amount_paise=450_000_00,
        days_overdue=60,
        days_since_last_contact=25,
        broken_promises_count=2,
        historical_recovery_rate=0.40,
        credit_score=550,
        relationship_tier=RelationshipTier.HIGH_RISK,
    )
    assert pred.recovery_probability <= 0.35
    assert pred.risk_band == "CRITICAL"
    assert pred.suggested_tone in (ToneType.FIRM, ToneType.URGENT)
