"""Deterministic Risk Scorer for B2B Receivables.

Calculates composite risk score (0-100) based on:
1. Overdue duration & amount exposure
2. Inactivity decay (days since last debtor engagement)
3. Promise credibility (broken promise history)
4. Customer credit score & relationship tier
"""

from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from src.models.db_models import RelationshipTier, PromiseStatus


class RiskScorer:
    """Calculates risk score (0 to 100) and assigns risk band."""

    @staticmethod
    def calculate_risk(
        amount_paise: int,
        days_overdue: int,
        days_since_last_contact: int,
        broken_promises_count: int,
        active_promises_count: int,
        credit_score: int = 700,
        historical_recovery_rate: float = 0.85,
        relationship_tier: RelationshipTier = RelationshipTier.STANDARD,
    ) -> Tuple[float, str, Dict[str, float]]:
        """
        Returns:
            (risk_score, risk_band, factor_breakdown)
        """
        # 1. Overdue Severity (0 - 30 points)
        if days_overdue <= 0:
            overdue_score = 0.0
        elif days_overdue <= 7:
            overdue_score = 5.0
        elif days_overdue <= 15:
            overdue_score = 12.0
        elif days_overdue <= 30:
            overdue_score = 20.0
        elif days_overdue <= 60:
            overdue_score = 26.0
        else:
            overdue_score = 30.0

        # Exposure scaling (large amounts add up to +5 points)
        amount_lakhs = amount_paise / 100_000_00
        exposure_penalty = min(amount_lakhs * 0.5, 5.0)
        overdue_factor = min(overdue_score + exposure_penalty, 35.0)

        # 2. Inactivity Decay (0 - 25 points)
        # Silence from debtor accelerates risk
        if days_since_last_contact <= 2:
            inactivity_score = 0.0
        elif days_since_last_contact <= 5:
            inactivity_score = 5.0
        elif days_since_last_contact <= 10:
            inactivity_score = 12.0
        elif days_since_last_contact <= 20:
            inactivity_score = 18.0
        else:
            inactivity_score = 25.0

        # 3. Promise Credibility Factor (0 - 30 points)
        # Broken promises heavily penalize credibility
        broken_penalty = min(broken_promises_count * 15.0, 30.0)
        # Active promising relieves some immediate risk if no broken promises
        active_relief = 5.0 if (active_promises_count > 0 and broken_promises_count == 0) else 0.0
        credibility_factor = max(broken_penalty - active_relief, 0.0)

        # 4. Debtor Profile & Credit Adjustment (-15 to +15 points)
        # Higher credit score reduces risk
        credit_adj = (750 - max(300, min(900, credit_score))) * 0.04  # 900 -> -6, 600 -> +6
        # Historical track record
        history_adj = (1.0 - max(0.0, min(1.0, historical_recovery_rate))) * 15.0 - 5.0
        # Tier mitigation
        tier_adj = {
            RelationshipTier.ENTERPRISE_VIP: -8.0,
            RelationshipTier.KEY_ACCOUNT: -4.0,
            RelationshipTier.STANDARD: 0.0,
            RelationshipTier.HIGH_RISK: 10.0,
        }.get(relationship_tier, 0.0)

        profile_adj = credit_adj + history_adj + tier_adj

        # Composite computation
        raw_score = overdue_factor + inactivity_score + credibility_factor + profile_adj
        composite_score = round(max(0.0, min(100.0, raw_score)), 2)

        # Determine band
        if composite_score < 25.0:
            band = "LOW"
        elif composite_score < 50.0:
            band = "MEDIUM"
        elif composite_score < 75.0:
            band = "HIGH"
        else:
            band = "CRITICAL"

        breakdown = {
            "overdue_factor": round(overdue_factor, 2),
            "inactivity_score": round(inactivity_score, 2),
            "credibility_factor": round(credibility_factor, 2),
            "profile_adjustment": round(profile_adj, 2),
        }

        return composite_score, band, breakdown
