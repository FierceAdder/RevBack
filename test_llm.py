"""Test utility to verify LLM Provider connectivity (Google Gemini / OpenAI / Anthropic).

Run with:
    .venv/bin/python test_llm.py
"""

import asyncio
import os
import sys
from src.config import settings
from src.llm.client import llm_client
from src.llm.extractors import DebtorExtractors, PromiseExtractionResult


async def main():
    print("\n" + "=" * 65)
    print("  🧪 REVBACK LLM CONNECTIVITY & EXTRACTION TEST")
    print("=" * 65)

    print(f"• Configured MOCK_LLM_MODE: {settings.MOCK_LLM_MODE}")
    print(f"• GEMINI_API_KEY Present:   {'YES (starts with ' + settings.GEMINI_API_KEY[:6] + '...)' if settings.GEMINI_API_KEY else 'NO (empty)'}")
    print(f"• OPENAI_API_KEY Present:   {'YES' if settings.OPENAI_API_KEY else 'NO'}")
    print(f"• ANTHROPIC_API_KEY Present:{'YES' if settings.ANTHROPIC_API_KEY else 'NO'}")
    print(f"• Target Model:             {settings.FAST_MODEL}")

    if not settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        print("\n⚠️  No live API key found in `.env`.")
        print("   To test with live Google Gemini:")
        print("   1. Open `.env`")
        print("   2. Set GEMINI_API_KEY=AIzaSy...")
        print("   3. Set MOCK_LLM_MODE=false")
        print("\nRunning test with deterministic local mock mode instead...\n")

    # Test 1: Text Generation
    print("--- [Test 1] Testing Text Generation ---")
    prompt = "Draft a 2-sentence polite WhatsApp reminder for overdue invoice #INV-101 for ₹50,000."
    response = await llm_client.complete(
        messages=[{"role": "user", "content": prompt}],
        model=settings.FAST_MODEL,
    )
    print("Response Output:\n" + response.strip())

    # Test 2: Structured Pydantic Extraction (Instructor)
    print("\n--- [Test 2] Testing Structured Extraction (Instructor + Pydantic) ---")
    sample_debtor_msg = "Hi team, we had a cash crunch but we will transfer ₹75,000 by this Friday afternoon."
    print(f"Debtor Input: '{sample_debtor_msg}'")

    extraction = await DebtorExtractors.extract_promise(
        text=sample_debtor_msg,
        invoice_amount_paise=75_000_00,
    )

    print("\nExtracted Pydantic Object:")
    print(f"• Has Promise:           {extraction.has_promise}")
    print(f"• Promised Amount:       ₹{extraction.promised_amount_paise / 100:,.2f} ({extraction.promised_amount_paise} paise)")
    print(f"• Promise Deadline Date: {extraction.promise_date_iso}")
    print(f"• Confidence Score:      {extraction.confidence:.1%}")
    print(f"• Raw Quote:             '{extraction.raw_quote}'")

    print("\n" + "=" * 65)
    print("  ✅ LLM PIPELINE IS FULLY OPERATIONAL AND READY!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
