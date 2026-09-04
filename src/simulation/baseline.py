"""Static Rule-Based Dunning Baseline Engine.

Implements the standard merchant baseline: sends generic automated reminder emails
every 7 days up to 3 times, without payment plans, tone adaptation, or smart escalation.
"""

from typing import List, Dict, Any
from src.simulation.simulator import DebtorSimulator


class BaselineRunner:
    """Executes the standard static baseline strategy on invoices."""

    @classmethod
    def run_invoice(cls, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs up to 3 static reminder attempts for an invoice.
        """
        archetype = invoice["archetype"]
        is_disputed = invoice.get("is_disputed", False)
        amount_paise = invoice["amount_paise"]

        total_days = 0
        is_recovered = False
        recovered_amount = 0

        # Attempt up to 3 static dunning emails
        for attempt in range(1, 4):
            total_days += 7
            # Baseline never offers payment plans
            outcome, ratio, details = DebtorSimulator.simulate_response(
                archetype=archetype,
                intervention_level=min(attempt, 2),  # Baseline never goes beyond generic level 2 reminder
                payment_plan_offered=False,
                is_disputed=is_disputed,
            )

            if outcome in ("PAID_FULL", "PAID_INSTALLMENT"):
                is_recovered = True
                recovered_amount = int(amount_paise * ratio)
                total_days += details.get("days_delay", 0)
                break
            elif outcome == "DISPUTED":
                # Static systems ignore or stall disputes
                break

        return {
            "invoice_id": invoice["id"],
            "strategy": "STATIC_BASELINE",
            "is_recovered": is_recovered,
            "recovered_amount_paise": recovered_amount,
            "days_to_recovery": total_days if is_recovered else invoice["days_overdue"] + 30,
            "attempts": attempt,
            "cost_usd": 0.005 * attempt,  # Basic SendGrid transactional email cost
        }
