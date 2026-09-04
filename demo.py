"""Interactive CLI demonstration for RevBack (Phases 1 to 4).

Runs the LangGraph recovery agent across 3 realistic B2B recovery scenarios:
1. Standard Overdue Invoice -> Courtesy Nudge + Razorpay Link
2. Distressed Debtor -> Autonomous 3-Part Payment Plan structuring
3. Chronic Defaulter with Broken Promise -> Firm Escalation & Evidence Bundle
"""

import asyncio
import json
from datetime import datetime, timezone

from src.agent.graph import build_recovery_graph
from src.agent.tools import EvidenceBundler
from src.models.db_models import RelationshipTier, ToneType


def print_banner(title: str):
    print("\n" + "=" * 75)
    print(f"  🚀 {title.upper()}")
    print("=" * 75)


def print_section(title: str):
    print(f"\n--- {title} ---")


async def run_scenario_1():
    print_banner("Scenario 1: Early Overdue Enterprise Client (Collaborative Nudge)")
    print("Debtor: CloudScale Systems Pvt Ltd | Relationship: ENTERPRISE_VIP | Overdue: 8 days")
    print("Invoice: ₹1,80,000 | Previous Promises Broken: 0")

    agent = build_recovery_graph(interrupt_human=False)

    state = {
        "invoice_id": "inv_demo_001",
        "customer_id": "cust_demo_001",
        "customer_name": "CloudScale Systems Pvt Ltd",
        "customer_email": "accounts@cloudscale.in",
        "customer_phone": "+919876543210",
        "invoice_number": "INV-2026-CS01",
        "amount_paise": 180_000_00,  # ₹1.8 Lakhs
        "amount_paid_paise": 0,
        "due_date_str": "2026-08-28",
        "days_overdue": 8,
        "relationship_tier": "ENTERPRISE_VIP",
        "credit_score": 790,
        "historical_recovery_rate": 0.96,
        "current_stage": "INTAKE",
        "current_level": 1,
        "is_recovered": False,
        "is_disputed": False,
        "dispute_reason": None,
        "has_active_promise": False,
        "has_broken_promise": False,
        "confidence_score": 0.95,
        "messages": [],
        "audit_trail": [],
    }

    result = await agent.ainvoke(state)

    print_section("Agent Diagnosis & Assessment")
    print(f"• Risk Score:          {result['risk_score']}/100 ({result['risk_band']} RISK)")
    print(f"• Recovery Probability:{result['recovery_probability']:.1%}")
    print(f"• Selected Channel:    {result['selected_channel']}")
    print(f"• Selected Tone:       {result['selected_tone']}")
    print(f"• Razorpay Link:       {result['payment_link_url']}")

    print_section("Generated Debtor Outreach")
    print(result["last_message_content"])


async def run_scenario_2():
    print_banner("Scenario 2: Distressed Debtor Offered Structured Payment Plan")
    print("Debtor: QuickCargo Logistics | Relationship: STANDARD | Overdue: 28 days")
    print("Invoice: ₹3,50,000 | Current Level: 3 -> Advancing to Level 4 (Settlement Plan)")

    agent = build_recovery_graph(interrupt_human=False)

    state = {
        "invoice_id": "inv_demo_002",
        "customer_id": "cust_demo_002",
        "customer_name": "QuickCargo Logistics",
        "customer_email": "pay@quickcargo.in",
        "customer_phone": "+919811122233",
        "invoice_number": "INV-2026-QC99",
        "amount_paise": 350_000_00,  # ₹3.5 Lakhs
        "amount_paid_paise": 0,
        "due_date_str": "2026-08-08",
        "days_overdue": 28,
        "relationship_tier": "STANDARD",
        "credit_score": 670,
        "historical_recovery_rate": 0.78,
        "current_stage": "DIAGNOSE",
        "current_level": 3,
        "is_recovered": False,
        "is_disputed": False,
        "dispute_reason": None,
        "has_active_promise": False,
        "has_broken_promise": False,
        "confidence_score": 0.90,
        "messages": [],
        "audit_trail": [],
    }

    result = await agent.ainvoke(state)

    print_section("Autonomous Payment Plan Proposal")
    plan = result["payment_plan_details"]
    print(f"• Summary: {plan['terms_summary']}")
    print("• Installment Schedule:")
    for inst in plan["installments"]:
        print(f"   [Installment {inst['installment_number']}]: {inst['amount_inr']} due on {inst['due_date_iso'][:10]} ({inst['status']})")

    print_section("Outreach Message Prepared")
    print(result["last_message_content"])


async def run_scenario_3():
    print_banner("Scenario 3: Chronic Defaulter with Broken Promise & Evidence Bundle")
    print("Debtor: OmniTech Manufacturing | Relationship: HIGH_RISK | Overdue: 55 days")
    print("Invoice: ₹5,00,000 | Status: Broke previous promise to pay by Friday")

    agent = build_recovery_graph(interrupt_human=False)

    state = {
        "invoice_id": "inv_demo_003",
        "customer_id": "cust_demo_003",
        "customer_name": "OmniTech Manufacturing",
        "customer_email": "cfo@omnitech.in",
        "customer_phone": "+919988776655",
        "invoice_number": "INV-2026-OMNI",
        "amount_paise": 500_000_00,  # ₹5 Lakhs
        "amount_paid_paise": 0,
        "due_date_str": "2026-07-12",
        "days_overdue": 55,
        "relationship_tier": "HIGH_RISK",
        "credit_score": 540,
        "historical_recovery_rate": 0.40,
        "current_stage": "DIAGNOSE",
        "current_level": 4,
        "is_recovered": False,
        "is_disputed": False,
        "dispute_reason": None,
        "has_active_promise": False,
        "has_broken_promise": True,  # Breached commitment!
        "confidence_score": 0.93,
        "messages": [],
        "audit_trail": [],
    }

    result = await agent.ainvoke(state)

    print_section("Escalation & Policy Outcome")
    print(f"• Escalated Level:     Level {result['current_level']} ({result['selected_channel']})")
    print(f"• Tone Selected:       {result['selected_tone']}")
    print(f"• Human Sign-off:      {result['requires_human_approval']} (Reason: {result['approval_reason']})")
    print(f"• Subject:             {result['last_message_subject']}")

    print_section("Compiled Bitemporal Evidence Bundle")
    bundle = EvidenceBundler.compile_evidence_bundle(
        invoice_number=result["invoice_number"],
        amount_paise=result["amount_paise"],
        customer_name=result["customer_name"],
        due_date_str=result["due_date_str"],
        audit_trail=result["audit_trail"],
        communications=result["messages"],
        promises=[{"status": "BROKEN", "amount_paise": 500_000_00, "quote": "We will transfer by Friday"}],
    )
    print(f"• Bundle Reference:   {bundle['evidence_bundle_id']}")
    print(f"• Certifying Notice:  {bundle['certifying_statement']}")
    print(f"• Audit Trail Events: {len(bundle['audit_trail'])} immutable timestamps recorded")


async def main():
    print("\n" + "#" * 75)
    print("  REVBACK — AI REVENUE RECOVERY AGENT (PHASES 1 - 4 LIVE DEMO)")
    print("#" * 75)
    await run_scenario_1()
    await run_scenario_2()
    await run_scenario_3()
    print("\n" + "=" * 75)
    print("  ✅ ALL 3 SCENARIOS COMPLETED AUTONOMOUSLY WITH ZERO ERRORS")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
