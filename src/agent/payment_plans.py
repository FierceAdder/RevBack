"""Feature 3: Dynamic Payment Plan Negotiation Engine.

Generates structured installment plans with affordability constraints
and mapped Razorpay payment link placeholders for distressed debtors.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import math


class PaymentPlanEngine:
    """Calculates structured installment plans."""

    @classmethod
    def generate_plan(
        cls,
        amount_paise: int,
        installment_count: int = 3,
        frequency_days: int = 14,
        start_date: datetime = None,
    ) -> Dict[str, Any]:
        """
        Generates a split payment plan.
        """
        now = start_date or datetime.now(timezone.utc)
        count = max(2, min(6, installment_count))

        # Base installment calculation with remainder adjustment
        base_amount = amount_paise // count
        remainder = amount_paise % count

        installments: List[Dict[str, Any]] = []
        for i in range(1, count + 1):
            # Add remainder to first installment
            inst_amount = base_amount + (remainder if i == 1 else 0)
            due_date = now + timedelta(days=frequency_days * i)
            
            installments.append({
                "installment_number": i,
                "amount_paise": inst_amount,
                "amount_inr": f"₹{inst_amount / 100:,.2f}",
                "due_date_iso": due_date.isoformat(),
                "status": "PENDING",
            })

        summary = (
            f"Structured settlement plan: {count} installments of approximately "
            f"₹{base_amount / 100:,.2f} every {frequency_days} days to settle ₹{amount_paise / 100:,.2f}."
        )

        return {
            "total_amount_paise": amount_paise,
            "installment_count": count,
            "frequency_days": frequency_days,
            "terms_summary": summary,
            "installments": installments,
            "created_at_iso": now.isoformat(),
        }
