"""LLM Client Router and Deterministic Mock Fallback.

Uses LiteLLM to route between models (Gemini Flash for extraction/classification,
GPT-4o/Claude for complex reasoning) with transparent fallback to deterministic
mock responses for offline testing, demos, and CI.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LiteLLM wrapper with fallback and mock test modes."""

    def __init__(self):
        self.mock_mode = settings.MOCK_LLM_MODE or not any(
            [settings.OPENAI_API_KEY, settings.ANTHROPIC_API_KEY, settings.GEMINI_API_KEY]
        )

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1000,
    ) -> str:
        """Standard text completion."""
        selected_model = model or settings.FAST_MODEL

        if not self.mock_mode:
            try:
                import litellm
                response = await litellm.acompletion(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"LiteLLM call to {selected_model} failed: {e}. Falling back to mock generator.")

        # Fallback / Mock completion
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        return self._generate_mock_completion(last_user_msg)

    def _generate_mock_completion(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "legal" in prompt_lower or "formal demand" in prompt_lower:
            return (
                "LEGAL DEMAND NOTICE\n\n"
                "To: The Director / Accounts Payable\n"
                "Subject: Demand for Immediate Settlement of Outstanding Dues\n\n"
                "Take notice that despite repeated reminders, the outstanding invoice remains unpaid. "
                "You are hereby called upon to remit the full amount within 7 days via the attached Razorpay link, "
                "failing which legal proceedings under applicable commercial dispute recovery laws will be initiated without further notice."
            )
        elif "whatsapp" in prompt_lower:
            return (
                "Hi there, gentle reminder regarding your pending invoice with our team. "
                "You can settle it seamlessly in 30 seconds using this secure Razorpay link: {{payment_link}}. "
                "Please let us know if you have any questions!"
            )
        else:
            return (
                "Dear Customer,\n\n"
                "We hope you are well. We are writing to follow up on your overdue invoice. "
                "Please click here to review and settle via Razorpay: {{payment_link}}.\n\n"
                "Best regards,\nRevBack Accounts Team"
            )


llm_client = LLMClient()
