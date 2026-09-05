"""LLM Client Router and Deterministic Mock Fallback.

Uses LiteLLM to route between models (Gemini Flash for extraction/classification,
GPT-4o/Claude for complex reasoning) with transparent fallback to deterministic
mock responses for offline testing, demos, and CI.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """LiteLLM wrapper with fallback and mock test modes."""

    def __init__(self):
        # Sync API keys from settings into environment variables for LiteLLM
        if settings.GEMINI_API_KEY:
            os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
        if settings.OPENAI_API_KEY:
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        if settings.ANTHROPIC_API_KEY:
            os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY

        # If mock mode is explicitly true, or no API keys exist, run in mock mode
        self.mock_mode = settings.MOCK_LLM_MODE or not any(
            [settings.OPENAI_API_KEY, settings.ANTHROPIC_API_KEY, settings.GEMINI_API_KEY]
        )
        self._instructor_client = None

        # Initialize Langfuse callbacks if keys are present
        try:
            from src.observability.langfuse import setup_langfuse
            setup_langfuse()
        except Exception:
            pass

    def _get_instructor(self):
        if self._instructor_client is None:
            import instructor
            import litellm
            self._instructor_client = instructor.from_litellm(litellm.acompletion)
        return self._instructor_client

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
                    api_key=settings.GEMINI_API_KEY if "gemini" in selected_model else None,
                )
                content = response.choices[0].message.content or ""
                # Record metrics if usage available
                try:
                    from src.observability.metrics import record_llm_tokens
                    from src.evaluation.cost_tracker import CostTracker
                    p_toks = getattr(response.usage, "prompt_tokens", 0) or 0
                    c_toks = getattr(response.usage, "completion_tokens", 0) or 0
                    record_llm_tokens(selected_model, p_toks, c_toks)
                    CostTracker.record_usage(selected_model, p_toks, c_toks)
                except Exception:
                    pass
                return content
            except Exception as e:
                logger.warning(f"LiteLLM call to {selected_model} failed: {e}. Falling back to mock generator.")

        # Fallback / Mock completion
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        mock_output = self._generate_mock_completion(last_user_msg)
        try:
            from src.observability.metrics import record_llm_tokens
            from src.evaluation.cost_tracker import CostTracker
            est_p = max(10, len(last_user_msg) // 4)
            est_c = max(10, len(mock_output) // 4)
            record_llm_tokens(selected_model, est_p, est_c)
            CostTracker.record_usage(selected_model, est_p, est_c)
        except Exception:
            pass
        return mock_output

    async def complete_structured(
        self,
        response_model: Type[T],
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Optional[T]:
        """Structured completion using Instructor + LiteLLM."""
        if self.mock_mode:
            return None

        selected_model = model or settings.FAST_MODEL
        try:
            client = self._get_instructor()
            result = await client.chat.completions.create(
                model=selected_model,
                response_model=response_model,
                messages=messages,
                temperature=temperature,
                api_key=settings.GEMINI_API_KEY if "gemini" in selected_model else None,
            )
            return result
        except Exception as e:
            logger.warning(f"Structured extraction call to {selected_model} failed: {e}")
            return None

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
