"""Financial and Operational Recovery Metrics Calculation."""

from typing import List, Dict, Any


class MetricCalculator:
    """Calculates summary KPIs from invoice outcome logs."""

    @classmethod
    def compute_strategy_metrics(
        cls,
        strategy_name: str,
        invoices: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Computes aggregate metrics for a strategy.
        """
        total_invoices = len(invoices)
        total_at_risk_paise = sum(inv["amount_paise"] for inv in invoices)

        recovered_count = sum(1 for r in results if r["is_recovered"])
        total_recovered_paise = sum(r["recovered_amount_paise"] for r in results)
        recovery_rate_pct = (recovered_count / total_invoices * 100.0) if total_invoices else 0.0

        recovered_results = [r for r in results if r["is_recovered"]]
        avg_days = (
            sum(r["days_to_recovery"] for r in recovered_results) / len(recovered_results)
            if recovered_results else 0.0
        )

        total_cost_usd = sum(r.get("cost_usd", 0.0) for r in results)
        broken_promises = sum(r.get("broken_promises_count", 0) for r in results)
        legal_escalations = sum(r.get("legal_escalations_count", 0) for r in results)

        return {
            "strategy_name": strategy_name,
            "total_invoices": total_invoices,
            "total_at_risk_paise": total_at_risk_paise,
            "total_at_risk_inr": f"₹{total_at_risk_paise / 100:,.2f}",
            "recovered_count": recovered_count,
            "total_recovered_paise": total_recovered_paise,
            "total_recovered_inr": f"₹{total_recovered_paise / 100:,.2f}",
            "recovery_rate_pct": round(recovery_rate_pct, 1),
            "average_days_to_recovery": round(avg_days, 1),
            "cost_spent_usd": round(total_cost_usd, 4),
            "cost_spent_inr": round(total_cost_usd * 84.0, 2),
            "broken_promises_count": broken_promises,
            "legal_escalations_count": legal_escalations,
        }
