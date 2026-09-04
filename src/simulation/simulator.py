"""Probabilistic Debtor Response Simulator.

Simulates how distinct Indian B2B debtor archetypes react to different
intervention levels, tone profiles, and structured payment plan proposals.
"""

import random
from typing import Dict, Any, Tuple


class DebtorSimulator:
    """Simulates debtor behavioral responses to communications."""

    @classmethod
    def simulate_response(
        cls,
        archetype: str,
        intervention_level: int,
        payment_plan_offered: bool,
        is_disputed: bool,
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Returns:
            (outcome, settlement_ratio, details)
            outcomes: "PAID_FULL", "PAID_INSTALLMENT", "PROMISED", "BROKE_PROMISE", "DISPUTED", "IGNORED"
        """
        roll = random.random()

        # 1. Disputed invoices
        if is_disputed:
            return "DISPUTED", 0.0, {
                "message": "We have an ongoing dispute regarding unit quantities billed. Please resolve before demanding payment.",
                "days_delay": 14,
            }

        # 2. Archetype Behaviors
        if archetype == "PROMPT_PAYER":
            if intervention_level in (1, 2):
                if roll < 0.85:
                    return "PAID_FULL", 1.0, {"message": "Payment transferred via Razorpay link. UTR attached.", "days_delay": 2}
                else:
                    return "PROMISED", 0.0, {"message": "Will process payment this Friday afternoon.", "days_delay": 4}
            else:
                return "PAID_FULL", 1.0, {"message": "Payment cleared in full.", "days_delay": 1}

        elif archetype == "CASH_STRAPPED":
            if payment_plan_offered:
                # High acceptance when offered structured installments
                if roll < 0.88:
                    return "PAID_INSTALLMENT", 1.0, {
                        "message": "Thank you for the installment option. First installment cleared via Razorpay.",
                        "days_delay": 14,
                    }
                else:
                    return "PROMISED", 0.0, {"message": "Reviewing installment plan with accounts.", "days_delay": 7}
            elif intervention_level <= 3:
                return "PROMISED", 0.0, {
                    "message": "Experiencing temporary cash crunch. Can we split the bill into installments?",
                    "days_delay": 10,
                }
            else:
                # Under heavy pressure without a plan, low recovery
                if roll < 0.35:
                    return "PAID_FULL", 1.0, {"message": "Scrambled funds to settle account.", "days_delay": 25}
                else:
                    return "IGNORED", 0.0, {"message": None, "days_delay": 30}

        elif archetype == "CHRONIC_DELAYER":
            if intervention_level <= 2:
                # Makes empty promise early
                return "BROKE_PROMISE", 0.0, {
                    "message": "Yes, we will definitely clear this by Monday.",
                    "days_delay": 7,
                }
            elif intervention_level in (3, 4, 5):
                if roll < 0.65:
                    return "PAID_FULL", 1.0, {"message": "Settled in full after overdue notice.", "days_delay": 18}
                else:
                    return "BROKE_PROMISE", 0.0, {"message": "Payment in pipeline, hold on.", "days_delay": 12}
            else:  # Level 6 Legal Notice
                if roll < 0.80:
                    return "PAID_FULL", 1.0, {"message": "Immediate settlement remitted upon receipt of legal notice.", "days_delay": 8}
                else:
                    return "IGNORED", 0.0, {"message": None, "days_delay": 45}

        elif archetype == "DISPUTER":
            # If dispute is addressed or escalated to human
            if roll < 0.70:
                return "PAID_FULL", 0.90, {"message": "Settled with adjusted credit note.", "days_delay": 20}
            else:
                return "DISPUTED", 0.0, {"message": "Legal dispute filed.", "days_delay": 60}

        else:  # GHOST_DEFAULTER
            if intervention_level < 6:
                return "IGNORED", 0.0, {"message": None, "days_delay": 30}
            else:
                # Level 6 Formal Demand Notice has teeth
                if roll < 0.45:
                    return "PAID_FULL", 1.0, {"message": "Settled immediately to prevent statutory legal action.", "days_delay": 10}
                else:
                    return "IGNORED", 0.0, {"message": None, "days_delay": 90}
