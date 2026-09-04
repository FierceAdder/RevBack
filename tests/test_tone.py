"""Unit tests for ToneEngine (Feature 1)."""

from src.llm.tone import ToneEngine
from src.models.db_models import RelationshipTier, ToneType


def test_tone_for_vip_customer():
    """VIP enterprise accounts receive collaborative tone early on."""
    analysis = ToneEngine.analyze_tone(
        relationship_tier=RelationshipTier.ENTERPRISE_VIP,
        risk_score=20.0,
        days_overdue=8,
        broken_promises_count=0,
        is_disputed=False,
    )
    assert analysis.recommended_tone == ToneType.COLLABORATIVE
    assert "VIP" in analysis.rationale


def test_tone_for_broken_promises():
    """Broken promises force tone escalation to FIRM or URGENT."""
    analysis_single_break = ToneEngine.analyze_tone(
        relationship_tier=RelationshipTier.STANDARD,
        risk_score=45.0,
        days_overdue=16,
        broken_promises_count=1,
        is_disputed=False,
    )
    assert analysis_single_break.recommended_tone == ToneType.FIRM

    analysis_double_break = ToneEngine.analyze_tone(
        relationship_tier=RelationshipTier.STANDARD,
        risk_score=70.0,
        days_overdue=35,
        broken_promises_count=2,
        is_disputed=False,
    )
    assert analysis_double_break.recommended_tone == ToneType.URGENT


def test_tone_for_disputed_invoice():
    """Disputed invoice requires professional non-adversarial reconciliation tone."""
    analysis = ToneEngine.analyze_tone(
        relationship_tier=RelationshipTier.STANDARD,
        risk_score=50.0,
        days_overdue=25,
        broken_promises_count=0,
        is_disputed=True,
    )
    assert analysis.recommended_tone == ToneType.PROFESSIONAL
    assert "Dispute" in analysis.rationale
