"""Feature 7: Confidence Gating for AI Actions.

Prevents autonomous actions when extraction or classification confidence
falls below safety thresholds, automatically escalating to human review.
"""

from typing import Dict
from src.models.schemas import GateResult
from src.config import settings


class ConfidenceGate:
    """Evaluates whether an AI extraction or decision meets safety thresholds."""

    THRESHOLDS: Dict[str, float] = {
        "intent_classification": settings.CONFIDENCE_THRESHOLD_INTENT,
        "promise_extraction": settings.CONFIDENCE_THRESHOLD_PROMISE,
        "amount_extraction": settings.CONFIDENCE_THRESHOLD_AMOUNT,
        "dispute_detection": settings.CONFIDENCE_THRESHOLD_DISPUTE,
    }

    @classmethod
    def evaluate(
        cls,
        task: str,
        confidence: float,
        invoice_amount_paise: int,
    ) -> GateResult:
        """
        Evaluate if confidence satisfies the task threshold.
        Amounts above ₹5 Lakhs incur an extra 5% stricter threshold.
        """
        base_threshold = cls.THRESHOLDS.get(task, 0.85)

        # Dynamic escalation: large exposures require higher certainty
        if invoice_amount_paise > settings.LEGAL_ESCALATION_THRESHOLD_PAISE:
            effective_threshold = min(base_threshold + 0.05, 0.98)
        else:
            effective_threshold = base_threshold

        passed = confidence >= effective_threshold

        if passed:
            return GateResult(
                passed=True,
                action="proceed",
                task=task,
                confidence=round(confidence, 4),
                threshold=round(effective_threshold, 4),
                reason=f"{task} confidence {confidence:.1%} meets threshold {effective_threshold:.1%}",
                invoice_amount=invoice_amount_paise,
            )
        else:
            return GateResult(
                passed=False,
                action="route_to_human",
                task=task,
                confidence=round(confidence, 4),
                threshold=round(effective_threshold, 4),
                reason=(
                    f"Confidence {confidence:.1%} is below required safety threshold {effective_threshold:.1%} "
                    f"for task '{task}' on invoice of ₹{invoice_amount_paise / 100:,.2f}"
                ),
                invoice_amount=invoice_amount_paise,
            )
