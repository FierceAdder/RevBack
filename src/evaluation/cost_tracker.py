"""Feature 6: Cost-per-Recovery & ROI Analytics Engine.

Measures the exact financial viability of AI recovery:
Token Spend (USD & INR) vs Recovered Capital (INR), calculating
Net Recovery Gain, Cost-per-Recovery %, and Return on Investment (ROI) Multiplier.
"""

from typing import Dict, Any


class CostTracker:
    """Calculates ROI and cost efficiency metrics."""

    USD_TO_INR_EXCHANGE_RATE = 84.0  # ₹84 per USD

    @classmethod
    def calculate_roi(
        cls,
        recovered_paise: int,
        total_token_cost_usd: float,
    ) -> Dict[str, Any]:
        """
        Calculates Net Recovery and ROI Multiplier.
        """
        recovered_inr = recovered_paise / 100.0
        cost_inr = total_token_cost_usd * cls.USD_TO_INR_EXCHANGE_RATE

        net_recovery_inr = max(0.0, recovered_inr - cost_inr)
        
        # Cost per ₹100 recovered
        if recovered_inr > 0:
            cost_percentage = (cost_inr / recovered_inr) * 100.0
            roi_multiple = recovered_inr / max(0.01, cost_inr)
        else:
            cost_percentage = 0.0
            roi_multiple = 0.0

        return {
            "recovered_inr": round(recovered_inr, 2),
            "token_cost_usd": round(total_token_cost_usd, 4),
            "token_cost_inr": round(cost_inr, 2),
            "net_recovery_inr": round(net_recovery_inr, 2),
            "cost_per_recovery_pct": round(cost_percentage, 3),  # e.g. 0.05% of recovered capital
            "roi_multiple": round(roi_multiple, 1),              # e.g. 185x ROI
        }
