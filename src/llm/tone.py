"""Feature 1: Smart Tone Adaptation Engine.

Dynamically adapts communication persona, formality, and linguistic style
based on customer tier, overdue duration, broken promise history, and risk score.
"""

from typing import Dict, Any
from src.models.db_models import RelationshipTier, ToneType
from src.models.schemas import ToneAnalysis


class ToneEngine:
    """Selects and formulates appropriate communication tone."""

    TONE_PROFILES: Dict[ToneType, Dict[str, Any]] = {
        ToneType.COLLABORATIVE: {
            "persona": "Helpful Partner",
            "formality_level": 2,
            "focus": "Mutual relationship, convenience of digital payment links, support with queries",
            "avoid": "Threats, aggressive language, mention of legal action or penalties",
        },
        ToneType.PROFESSIONAL: {
            "persona": "Corporate Accounts Officer",
            "formality_level": 3,
            "focus": "Clear invoice details, transaction reconciliation, standard payment terms",
            "avoid": "Overly casual greetings or premature escalation",
        },
        ToneType.FIRM: {
            "persona": "Credit Control Manager",
            "formality_level": 4,
            "focus": "Specific overdue duration, impact on credit account status, required settlement timeline",
            "avoid": "Vagueness or unearned pleasantries",
        },
        ToneType.URGENT: {
            "persona": "Senior Recovery Lead",
            "formality_level": 4,
            "focus": "Immediate action required, risk of service interruption, imminent legal handover",
            "avoid": "Indecisive language or open-ended timelines",
        },
        ToneType.FORMAL_LEGAL: {
            "persona": "Legal & Compliance Counsel",
            "formality_level": 5,
            "focus": "Statutory notice of default, formal demand for full remittance, reservation of legal rights",
            "avoid": "Informal phrasing, discounts, or compromise outside formal agreements",
        },
    }

    @classmethod
    def analyze_tone(
        cls,
        relationship_tier: RelationshipTier,
        risk_score: float,
        days_overdue: int,
        broken_promises_count: int,
        is_disputed: bool,
    ) -> ToneAnalysis:
        """
        Determines the optimal tone profile.
        """
        if is_disputed:
            return ToneAnalysis(
                persona="Customer Solutions Arbitrator",
                recommended_tone=ToneType.PROFESSIONAL,
                rationale="Dispute requires objective, non-accusatory reconciliation.",
                formality_level=3,
            )

        # VIP accounts receive collaborative treatment longer
        if relationship_tier == RelationshipTier.ENTERPRISE_VIP and days_overdue < 30 and broken_promises_count == 0:
            return ToneAnalysis(
                persona=cls.TONE_PROFILES[ToneType.COLLABORATIVE]["persona"],
                recommended_tone=ToneType.COLLABORATIVE,
                rationale="Enterprise VIP account: prioritize relationship preservation and soft nudges.",
                formality_level=2,
            )

        # Broken promises trigger immediate escalation to FIRM or URGENT
        if broken_promises_count >= 2:
            return ToneAnalysis(
                persona=cls.TONE_PROFILES[ToneType.URGENT]["persona"],
                recommended_tone=ToneType.URGENT,
                rationale=f"Customer breached {broken_promises_count} payment commitments.",
                formality_level=4,
            )
        elif broken_promises_count == 1:
            return ToneAnalysis(
                persona=cls.TONE_PROFILES[ToneType.FIRM]["persona"],
                recommended_tone=ToneType.FIRM,
                rationale="Customer missed previous promise to pay; firm urgency required.",
                formality_level=4,
            )

        # Risk Score & Overdue mapping
        if risk_score >= 80 or days_overdue >= 60:
            tone = ToneType.FORMAL_LEGAL
            rationale = f"Critical risk score ({risk_score:.1f}) and {days_overdue} days overdue."
        elif risk_score >= 60 or days_overdue >= 30:
            tone = ToneType.URGENT
            rationale = f"Elevated risk score ({risk_score:.1f}) requires high-priority escalation."
        elif risk_score >= 35 or days_overdue >= 14:
            tone = ToneType.FIRM
            rationale = f"Moderate delay ({days_overdue} days overdue); firm professional tone."
        elif days_overdue >= 5:
            tone = ToneType.PROFESSIONAL
            rationale = "Recent due date expiry; standard professional reminder."
        else:
            tone = ToneType.COLLABORATIVE
            rationale = "Early stage receivable; collaborative friendly reminder."

        profile = cls.TONE_PROFILES[tone]
        return ToneAnalysis(
            persona=profile["persona"],
            recommended_tone=tone,
            rationale=rationale,
            formality_level=profile["formality_level"],
        )
