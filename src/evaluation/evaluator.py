"""Head-to-Head Comparative Evaluator.

Runs the Static Dunning Baseline and RevBack AI Agent on identical synthetic datasets,
computing Recovery Rate Uplift, DSO Reduction, and ROI Multipliers.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any

from src.simulation.baseline import BaselineRunner
from src.simulation.runner import AgentRunner
from src.evaluation.metrics import MetricCalculator
from src.evaluation.cost_tracker import CostTracker


class RecoveryEvaluator:
    """Orchestrates head-to-head evaluation between Baseline and Agent."""

    @classmethod
    async def evaluate_batch(
        cls,
        invoices: List[Dict[str, Any]],
        include_baseline: bool = True,
    ) -> Dict[str, Any]:
        """
        Runs both strategies on the provided invoice list and produces comparative report.
        """
        # 1. Run Baseline
        baseline_results = []
        if include_baseline:
            for inv in invoices:
                b_res = BaselineRunner.run_invoice(inv)
                baseline_results.append(b_res)

        baseline_metrics = MetricCalculator.compute_strategy_metrics(
            strategy_name="STATIC_ERP_BASELINE",
            invoices=invoices,
            results=baseline_results,
        ) if include_baseline else {}

        # 2. Run RevBack Agent
        agent_results = []
        for inv in invoices:
            a_res = await AgentRunner.run_invoice(inv)
            agent_results.append(a_res)

        agent_metrics = MetricCalculator.compute_strategy_metrics(
            strategy_name="REVBACK_AI_AGENT",
            invoices=invoices,
            results=agent_results,
        )

        # 3. Compute Comparative Uplift
        uplift_pp = 0.0
        dso_reduction = 0.0
        net_recovered_gain_paise = 0

        if include_baseline:
            uplift_pp = round(agent_metrics["recovery_rate_pct"] - baseline_metrics["recovery_rate_pct"], 1)
            dso_reduction = round(baseline_metrics["average_days_to_recovery"] - agent_metrics["average_days_to_recovery"], 1)
            net_recovered_gain_paise = agent_metrics["total_recovered_paise"] - baseline_metrics["total_recovered_paise"]

        # 4. Compute ROI Multiplier
        roi_stats = CostTracker.calculate_roi(
            recovered_paise=agent_metrics["total_recovered_paise"],
            total_token_cost_usd=agent_metrics["cost_spent_usd"],
        )

        return {
            "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "invoices_evaluated": len(invoices),
            "baseline": baseline_metrics,
            "agent": agent_metrics,
            "comparative": {
                "uplift_percentage_points": uplift_pp,
                "dso_reduction_days": dso_reduction,
                "additional_capital_recovered_inr": f"₹{net_recovered_gain_paise / 100:,.2f}",
                "additional_capital_recovered_paise": net_recovered_gain_paise,
                "roi_multiple": roi_stats["roi_multiple"],
                "cost_per_recovery_pct": roi_stats["cost_per_recovery_pct"],
                "token_cost_usd": roi_stats["token_cost_usd"],
                "token_cost_inr": roi_stats["token_cost_inr"],
            },
        }
