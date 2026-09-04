"""Synthetic B2B Receivable Dataset Generator for Indian Merchants.

Generates realistic B2B invoices across varied debtor archetypes:
1. PROMPT_PAYER (Settles on gentle reminder)
2. CASH_STRAPPED (Receptive to structured payment plans)
3. CHRONIC_DELAYER (Breaches early promises, responds to firm escalation)
4. DISPUTER (Questions charges, halts automated dunning)
5. GHOST_DEFAULTER (Unresponsive until formal legal demand notice)
"""

from datetime import datetime, timezone, timedelta
import random
from typing import List, Dict, Any

from src.models.db_models import RelationshipTier

INDIAN_B2B_COMPANIES = [
    ("Swadeshi Logistics Pvt Ltd", "B2B_LOGISTICS", RelationshipTier.STANDARD),
    ("Nexus Cloudworks India", "B2B_SAAS", RelationshipTier.ENTERPRISE_VIP),
    ("Zenith Heavy Engineering", "MANUFACTURING", RelationshipTier.KEY_ACCOUNT),
    ("Kaveri Agro Traders LLP", "WHOLESALE", RelationshipTier.STANDARD),
    ("Aura Digital Media Agency", "MARKETING", RelationshipTier.STANDARD),
    ("Prism Fintech Solutions", "FINTECH", RelationshipTier.ENTERPRISE_VIP),
    ("Vanguard Security Systems", "FACILITY_MGMT", RelationshipTier.STANDARD),
    ("Garuda Freight Carriers", "B2B_LOGISTICS", RelationshipTier.HIGH_RISK),
    ("Bharat TexFab Mills", "MANUFACTURING", RelationshipTier.STANDARD),
    ("Apex Clinical Laboratories", "HEALTHCARE", RelationshipTier.KEY_ACCOUNT),
    ("Trident Infra Projects Ltd", "CONSTRUCTION", RelationshipTier.HIGH_RISK),
    ("Falcon E-Commerce Warehousing", "ECOMMERCE", RelationshipTier.STANDARD),
]

ARCHETYPES = [
    "PROMPT_PAYER",
    "CASH_STRAPPED",
    "CHRONIC_DELAYER",
    "DISPUTER",
    "GHOST_DEFAULTER",
]

ARCHETYPE_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]


class DatasetGenerator:
    """Generates synthetic dataset of overdue B2B receivables."""

    @classmethod
    def generate_invoices(
        cls,
        count: int = 50,
        reference_date: datetime = None,
        seed: int = 42,
    ) -> List[Dict[str, Any]]:
        """Generates a reproducible list of overdue invoice records."""
        random.seed(seed)
        now = reference_date or datetime.now(timezone.utc)

        invoices = []
        for i in range(1, count + 1):
            company_name, business_type, default_tier = random.choice(INDIAN_B2B_COMPANIES)
            archetype = random.choices(ARCHETYPES, weights=ARCHETYPE_WEIGHTS)[0]

            # Invoices overdue between 5 and 75 days
            days_overdue = random.randint(5, 75)
            due_date = now - timedelta(days=days_overdue)

            # Amount in paise (₹25,000 to ₹12,50,000)
            amount_rupees = random.choice([
                25_000, 45_000, 75_000, 120_000, 180_000, 250_000, 350_000, 500_000, 850_000, 1_250_000
            ])
            amount_paise = amount_rupees * 100

            # Historical credit score and recovery rate by archetype
            if archetype == "PROMPT_PAYER":
                credit_score = random.randint(750, 850)
                historical_recovery = random.uniform(0.90, 0.99)
            elif archetype == "CASH_STRAPPED":
                credit_score = random.randint(620, 720)
                historical_recovery = random.uniform(0.70, 0.85)
            elif archetype == "CHRONIC_DELAYER":
                credit_score = random.randint(580, 680)
                historical_recovery = random.uniform(0.55, 0.75)
            elif archetype == "DISPUTER":
                credit_score = random.randint(650, 780)
                historical_recovery = random.uniform(0.65, 0.85)
            else:  # GHOST_DEFAULTER
                credit_score = random.randint(480, 600)
                historical_recovery = random.uniform(0.20, 0.45)

            clean_name_slug = company_name.lower().replace(" ", "").replace(".", "")[:8]
            invoice = {
                "id": f"inv_sim_{i:04d}",
                "invoice_number": f"INV-2026-{i:04d}",
                "customer_id": f"cust_sim_{clean_name_slug}_{i:03d}",
                "customer_name": f"{company_name} #{i}",
                "customer_email": f"finance_{i}@{clean_name_slug}.in",
                "customer_phone": f"+9198{random.randint(10000000, 99999999)}",
                "business_type": business_type,
                "relationship_tier": default_tier.value,
                "amount_paise": amount_paise,
                "amount_inr": f"₹{amount_rupees:,.2f}",
                "days_overdue": days_overdue,
                "due_date_iso": due_date.isoformat(),
                "due_date_str": due_date.strftime("%Y-%m-%d"),
                "archetype": archetype,
                "credit_score": credit_score,
                "historical_recovery_rate": round(historical_recovery, 2),
                "is_disputed": archetype == "DISPUTER" and random.random() < 0.7,
                "dispute_reason": "Billed unit quantity does not match approved purchase order delivery note" if archetype == "DISPUTER" else None,
            }
            invoices.append(invoice)

        return invoices
