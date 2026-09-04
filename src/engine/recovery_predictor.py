"""Feature 2: Recovery Probability Predictor.

Estimates the probability P(Recovery) in [0.0, 1.0] and recommends
the optimal recovery intervention trajectory based on risk factors.
"""

import math
from typing import Dict, Any
from src.models.db_models import RelationshipTier, ToneType
from src.models.schemas import RecoveryPrediction


class RecoveryPredictor:
    """Calibrated logistic probability model for receivable recovery."""

    @classmethod
    def predict(
        cls,
        amount_paise: int,
        days_overdue: int,
        days_since_last_contact: int,
        broken_promises_count: int,
        historical_recovery_rate: float,
        credit_score: int,
        relationship_tier: RelationshipTier,
    ) -> RecoveryPrediction:
        """
        Calculate recovery probability P(Recovery) using weighted logit score.
        """
        # Baseline logit (intercept corresponds to ~75% base B2B recovery)
        logit = 1.10

        # Overdue penalty: -0.05 per week overdue
        overdue_weeks = max(0, days_overdue) / 7.0
        logit -= 0.35 * overdue_weeks

        # Broken promises: severe hit (-0.75 per broken promise)
        logit -= 0.85 * broken_promises_count

        # Inactivity: -0.15 per week of silence
        inactivity_weeks = max(0, days_since_last_contact) / 7.0
        logit -= 0.25 * inactivity_weeks

        # Customer history boost
        history_delta = (historical_recovery_rate - 0.70) * 2.5
        logit += history_delta

        # Credit score adjustment
        credit_delta = (credit_score - 700) / 100.0 * 0.4
        logit += credit_delta

        # Relationship tier factor
        tier_weight = {
            RelationshipTier.ENTERPRISE_VIP: 0.5,
            RelationshipTier.KEY_ACCOUNT: 0.25,
            RelationshipTier.STANDARD: 0.0,
            RelationshipTier.HIGH_RISK: -0.6,
        }.get(relationship_tier, 0.0)
        logit += tier_weight

        # Sigmoid conversion
        probability = 1.0 / (1.0 + math.exp(-max(-6.0, min(6.0, logit))))
        probability = round(probability, 3)

        # Risk band & recommendation
        if probability >= 0.80:
            band = "LOW"
            suggested_level = 1
            suggested_tone = ToneType.COLLABORATIVE
            path = "GENTLE_COURTESY_REMINDER_WITH_PAYMENT_LINK"
        elif probability >= 0.55:
            band = "MEDIUM"
            suggested_level = 2
            suggested_tone = ToneType.PROFESSIONAL
            path = "STRUCTURED_INQUIRY_AND_PAYMENT_OPTIONS"
        elif probability >= 0.30:
            band = "HIGH"
            suggested_level = 4
            suggested_tone = ToneType.FIRM
            path = "INSTALLMENT_PLAN_OFFER_BEFORE_ESCALATION"
        else:
            band = "CRITICAL"
            suggested_level = 6
            suggested_tone = ToneType.URGENT
            path = "FORMAL_LEGAL_DEMAND_AND_CREDIT_BUREAU_NOTICE"

        factors = {
            "overdue_weeks": round(overdue_weeks, 1),
            "broken_promises": float(broken_promises_count),
            "historical_recovery_rate": round(historical_recovery_rate, 2),
            "credit_score": float(credit_score),
            "tier_weight": round(tier_weight, 2),
        }

        return RecoveryPrediction(
            recovery_probability=probability,
            risk_band=band,
            recommended_path=path,
            factors=factors,
            suggested_level=suggested_level,
            suggested_tone=suggested_tone,
        )
