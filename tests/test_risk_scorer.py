"""Unit tests for RiskScorer."""

from src.engine.risk_scorer import RiskScorer
from src.models.db_models import RelationshipTier


def test_low_risk_timely_invoice():
    """An invoice barely overdue with an enterprise VIP customer should be low risk."""
    score, band, breakdown = RiskScorer.calculate_risk(
        amount_paise=50_000_00,
        days_overdue=3,
        days_since_last_contact=1,
        broken_promises_count=0,
        active_promises_count=1,
        credit_score=800,
        historical_recovery_rate=0.98,
        relationship_tier=RelationshipTier.ENTERPRISE_VIP,
    )
    assert band == "LOW"
    assert score < 25.0
    assert breakdown["credibility_factor"] == 0.0


def test_high_risk_broken_promises_chronic_delay():
    """An invoice 45 days overdue with 2 broken promises must score critical or high."""
    score, band, breakdown = RiskScorer.calculate_risk(
        amount_paise=400_000_00,
        days_overdue=45,
        days_since_last_contact=15,
        broken_promises_count=2,
        active_promises_count=0,
        credit_score=580,
        historical_recovery_rate=0.45,
        relationship_tier=RelationshipTier.HIGH_RISK,
    )
    assert band in ("HIGH", "CRITICAL")
    assert score >= 70.0
    assert breakdown["credibility_factor"] >= 25.0


def test_score_bounded_between_0_and_100():
    """Edge cases should never exceed bounds [0, 100]."""
    # Worst case imaginable
    worst_score, worst_band, _ = RiskScorer.calculate_risk(
        amount_paise=100_000_000_00,
        days_overdue=180,
        days_since_last_contact=90,
        broken_promises_count=10,
        active_promises_count=0,
        credit_score=300,
        historical_recovery_rate=0.0,
        relationship_tier=RelationshipTier.HIGH_RISK,
    )
    assert worst_score == 100.0
    assert worst_band == "CRITICAL"

    # Best case
    best_score, best_band, _ = RiskScorer.calculate_risk(
        amount_paise=1000_00,
        days_overdue=0,
        days_since_last_contact=0,
        broken_promises_count=0,
        active_promises_count=1,
        credit_score=900,
        historical_recovery_rate=1.0,
        relationship_tier=RelationshipTier.ENTERPRISE_VIP,
    )
    assert best_score >= 0.0
    assert best_band == "LOW"
