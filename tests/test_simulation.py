"""Unit and integration tests for DatasetGenerator, DebtorSimulator, and Head-to-Head Evaluator."""

import pytest
from src.simulation.generator import DatasetGenerator
from src.simulation.simulator import DebtorSimulator
from src.simulation.baseline import BaselineRunner
from src.simulation.runner import AgentRunner
from src.evaluation.evaluator import RecoveryEvaluator
from src.evaluation.cost_tracker import CostTracker


def test_dataset_generator_distribution():
    """Verifies synthetic dataset generation produces realistic amounts and archetypes."""
    invoices = DatasetGenerator.generate_invoices(count=30, seed=123)

    assert len(invoices) == 30
    archetypes = {inv["archetype"] for inv in invoices}
    assert len(archetypes) >= 4  # Covers majority of archetypes
    assert all(inv["amount_paise"] >= 25_000_00 for inv in invoices)
    assert all(inv["days_overdue"] >= 5 for inv in invoices)
    assert all("INV-2026-" in inv["invoice_number"] for inv in invoices)


def test_debtor_simulator_cash_strapped():
    """Cash strapped debtor accepts when payment plan is offered."""
    # When plan offered
    outcome, ratio, _ = DebtorSimulator.simulate_response(
        archetype="CASH_STRAPPED",
        intervention_level=4,
        payment_plan_offered=True,
        is_disputed=False,
    )
    assert outcome in ("PAID_INSTALLMENT", "PROMISED")


def test_cost_tracker_roi_calculation():
    """Verifies ROI and cost per recovery math."""
    stats = CostTracker.calculate_roi(
        recovered_paise=1_000_000_00,  # ₹10 Lakhs in paise
        total_token_cost_usd=0.25,     # $0.25 (~₹21)
    )
    assert stats["recovered_inr"] == 1_000_000.0
    assert stats["token_cost_inr"] == 21.0
    assert stats["roi_multiple"] > 1000.0
    assert stats["cost_per_recovery_pct"] < 0.01  # Fraction of 1%


@pytest.mark.asyncio
async def test_head_to_head_comparative_uplift():
    """Verifies agent outperforms static baseline on identical batch of invoices."""
    invoices = DatasetGenerator.generate_invoices(count=20, seed=42)

    report = await RecoveryEvaluator.evaluate_batch(invoices, include_baseline=True)

    baseline = report["baseline"]
    agent = report["agent"]
    comparative = report["comparative"]

    # Verify report structure
    assert report["invoices_evaluated"] == 20
    assert baseline["recovery_rate_pct"] >= 0.0
    assert agent["recovery_rate_pct"] >= baseline["recovery_rate_pct"]  # Agent wins or ties!
    assert comparative["roi_multiple"] > 10.0  # Massive financial return on LLM tokens
    assert comparative["token_cost_inr"] > 0
