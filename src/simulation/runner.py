"""RevBack Autonomous Agent Simulation Runner.

Executes the LangGraph recovery cycle across a batch of invoices, simulating
debtor reactions, tracking promise fulfillment, and generating financial metrics.
"""

from typing import Dict, Any, List
from src.agent.graph import build_recovery_graph
from src.simulation.simulator import DebtorSimulator


class AgentRunner:
    """Simulates agent-driven recovery workflow across invoices."""

    @classmethod
    async def run_invoice(cls, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes multi-turn agent recovery on a single invoice.
        """
        agent = build_recovery_graph(interrupt_human=False)

        amount_paise = invoice["amount_paise"]
        archetype = invoice["archetype"]
        is_disputed = invoice.get("is_disputed", False)

        current_level = 1
        has_broken_promise = False
        is_recovered = False
        recovered_amount = 0
        total_days = 0
        broken_promises_count = 0
        legal_escalations_count = 0
        token_cost_usd = 0.0

        # Run up to 5 multi-turn agent recovery cycles
        for cycle in range(1, 6):
            state = {
                "invoice_id": invoice["id"],
                "customer_id": invoice["customer_id"],
                "customer_name": invoice["customer_name"],
                "customer_email": invoice["customer_email"],
                "customer_phone": invoice["customer_phone"],
                "invoice_number": invoice["invoice_number"],
                "amount_paise": amount_paise,
                "amount_paid_paise": 0,
                "due_date_str": invoice["due_date_str"],
                "days_overdue": invoice["days_overdue"] + total_days,
                "relationship_tier": invoice["relationship_tier"],
                "credit_score": invoice["credit_score"],
                "historical_recovery_rate": invoice["historical_recovery_rate"],
                "current_stage": "INTAKE" if cycle == 1 else "DIAGNOSE",
                "current_level": current_level,
                "is_recovered": False,
                "is_disputed": is_disputed and cycle == 1,
                "dispute_reason": invoice.get("dispute_reason"),
                "has_active_promise": False,
                "has_broken_promise": has_broken_promise,
                "confidence_score": 0.95,
                "messages": [],
                "audit_trail": [],
            }

            # Invoke agent
            result = await agent.ainvoke(state)
            current_level = result["current_level"]
            payment_plan_offered = result.get("payment_plan_offered", False)
            token_cost_usd += 0.0015  # Token cost per turn (~1500 tokens on Gemini Flash)

            if current_level >= 6:
                legal_escalations_count += 1

            # Simulate debtor reaction to agent's intervention
            outcome, ratio, details = DebtorSimulator.simulate_response(
                archetype=archetype,
                intervention_level=current_level,
                payment_plan_offered=payment_plan_offered,
                is_disputed=is_disputed and cycle == 1,
            )

            total_days += details.get("days_delay", 5)

            if outcome in ("PAID_FULL", "PAID_INSTALLMENT"):
                is_recovered = True
                recovered_amount = int(amount_paise * ratio)
                break
            elif outcome == "BROKE_PROMISE":
                has_broken_promise = True
                broken_promises_count += 1
                current_level = min(current_level + 2, 6)
            elif outcome == "DISPUTED":
                # Agent resolves dispute by next cycle
                is_disputed = False
                current_level = 2

        return {
            "invoice_id": invoice["id"],
            "strategy": "REVBACK_AI_AGENT",
            "is_recovered": is_recovered,
            "recovered_amount_paise": recovered_amount,
            "days_to_recovery": total_days if is_recovered else invoice["days_overdue"] + 45,
            "cycles": cycle,
            "broken_promises_count": broken_promises_count,
            "legal_escalations_count": legal_escalations_count,
            "cost_usd": round(token_cost_usd, 4),
        }
