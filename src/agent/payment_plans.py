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
        relationship_tier: Any = None,
        broken_promises_count: int = 0,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generates a split payment plan.
        """
        now = start_date or datetime.now(timezone.utc)
        if broken_promises_count > 0:
            count = 2
        elif relationship_tier and getattr(relationship_tier, "value", str(relationship_tier)) == "VIP":
            count = 4
        else:
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

    @classmethod
    async def generate_plan_with_links(
        cls,
        amount_paise: int,
        invoice_number: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Any = None,
        installment_count: int = 3,
        frequency_days: int = 14,
        start_date: Any = None,
    ) -> Dict[str, Any]:
        """Generates structured payment plan with live per-installment Razorpay payment links and expiration dates."""
        from src.agent.tools import RazorpayTools

        plan = cls.generate_plan(
            amount_paise=amount_paise,
            installment_count=installment_count,
            frequency_days=frequency_days,
            start_date=start_date,
        )

        for inst in plan["installments"]:
            due_dt = datetime.fromisoformat(inst["due_date_iso"])
            expire_timestamp = int(due_dt.timestamp())
            link_data = await RazorpayTools.create_payment_link(
                amount_paise=inst["amount_paise"],
                invoice_number=f"{invoice_number}-INST-{inst['installment_number']}",
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                description=f"Installment {inst['installment_number']}/{plan['installment_count']} for Invoice #{invoice_number}",
                expire_by=expire_timestamp,
            )
            inst["razorpay_payment_link_id"] = link_data["payment_link_id"]
            inst["payment_link_url"] = link_data["payment_link_url"]

        return plan

