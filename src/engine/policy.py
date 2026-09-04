"""Deterministic Policy Engine for AI Revenue Recovery.

Governs intervention levels (1 through 7), cooldown rules, frequency caps,
channel selection, and human approval escalation gates.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from src.models.db_models import (
    RelationshipTier, CommunicationChannel, ToneType, InvoiceStatus
)


class PolicyDecision:
    def __init__(
        self,
        should_act: bool,
        next_level: int,
        channel: CommunicationChannel,
        tone: ToneType,
        requires_human_approval: bool,
        reason: str,
        cooldown_remaining_hours: float = 0.0,
    ):
        self.should_act = should_act
        self.next_level = next_level
        self.channel = channel
        self.tone = tone
        self.requires_human_approval = requires_human_approval
        self.reason = reason
        self.cooldown_remaining_hours = cooldown_remaining_hours

    def to_dict(self) -> Dict[str, Any]:
        return {
            "should_act": self.should_act,
            "next_level": self.next_level,
            "channel": self.channel.value,
            "tone": self.tone.value,
            "requires_human_approval": self.requires_human_approval,
            "reason": self.reason,
            "cooldown_remaining_hours": round(self.cooldown_remaining_hours, 1),
        }


class PolicyEngine:
    """Evaluates invoice state against deterministic compliance & recovery rules."""

    COOLDOWN_DAYS_PER_LEVEL = {
        1: 3,  # Level 1 -> 2
        2: 3,  # Level 2 -> 3
        3: 4,  # Level 3 -> 4
        4: 5,  # Level 4 -> 5
        5: 5,  # Level 5 -> 6
        6: 7,  # Level 6 -> 7
        7: 14,
    }

    @classmethod
    def evaluate_next_action(
        cls,
        current_level: int,
        days_overdue: int,
        last_contact_time: Optional[datetime],
        has_active_promise: bool,
        has_broken_promise: bool,
        is_disputed: bool,
        amount_paise: int,
        relationship_tier: RelationshipTier = RelationshipTier.STANDARD,
        now: Optional[datetime] = None,
    ) -> PolicyDecision:
        """
        Calculates whether to intervene, what level and channel to use, and if human approval is needed.
        """
        current_time = now or datetime.now(timezone.utc)

        # 1. Hard Rule: If invoice is already disputed, halt automated collection
        if is_disputed:
            return PolicyDecision(
                should_act=False,
                next_level=current_level,
                channel=CommunicationChannel.EMAIL,
                tone=ToneType.PROFESSIONAL,
                requires_human_approval=True,
                reason="Invoice is actively disputed. Automated recovery halted pending dispute resolution.",
            )

        # 2. Hard Rule: If active promise to pay is pending within grace period, do not harass debtor
        if has_active_promise:
            return PolicyDecision(
                should_act=False,
                next_level=current_level,
                channel=CommunicationChannel.WHATSAPP,
                tone=ToneType.COLLABORATIVE,
                requires_human_approval=False,
                reason="Active promise to pay is in progress. Outbound reminders suspended.",
            )

        # 3. Check Cooldown period since last contact
        if last_contact_time is not None:
            required_days = cls.COOLDOWN_DAYS_PER_LEVEL.get(current_level, 3)
            time_since_contact = current_time - last_contact_time
            required_duration = timedelta(days=required_days)

            if time_since_contact < required_duration and not has_broken_promise:
                remaining_hours = (required_duration - time_since_contact).total_seconds() / 3600.0
                return PolicyDecision(
                    should_act=False,
                    next_level=current_level,
                    channel=CommunicationChannel.EMAIL,
                    tone=ToneType.COLLABORATIVE,
                    requires_human_approval=False,
                    reason=f"Cooldown active. Must wait {required_days} days between Level {current_level} contacts.",
                    cooldown_remaining_hours=remaining_hours,
                )

        # 4. Determine Next Level
        if has_broken_promise:
            # Accelerated escalation on broken promise
            next_level = min(current_level + 2, 6)
            reason = f"Debtor breached promise to pay. Escalating to Level {next_level}."
        else:
            next_level = min(current_level + 1, 7) if days_overdue > 0 else 1
            reason = f"Progressing to Level {next_level} due to {days_overdue} days overdue."

        # 5. Channel Selection by Level and Tier
        if relationship_tier == RelationshipTier.ENTERPRISE_VIP and next_level < 5:
            # VIP accounts get executive email or relationship manager outreach
            channel = CommunicationChannel.EMAIL
        elif next_level in (1, 2):
            channel = CommunicationChannel.WHATSAPP
        elif next_level in (3, 4):
            channel = CommunicationChannel.EMAIL
        elif next_level == 5:
            channel = CommunicationChannel.SMS
        else:
            channel = CommunicationChannel.FORMAL_NOTICE

        # 6. Tone Mapping
        if next_level == 1:
            tone = ToneType.COLLABORATIVE
        elif next_level in (2, 3):
            tone = ToneType.PROFESSIONAL
        elif next_level in (4, 5):
            tone = ToneType.FIRM
        elif next_level == 6:
            tone = ToneType.URGENT
        else:
            tone = ToneType.FORMAL_LEGAL

        # 7. Human-in-the-Loop Escalation Rules
        # Levels 6 (Demand notice) and 7 (Legal escalation), or amounts > ₹5 Lakh at Level 5+ require human review
        requires_approval = False
        if next_level >= 6:
            requires_approval = True
            reason += " Legal notice or collections escalation requires human sign-off."
        elif next_level >= 4 and amount_paise >= 500_000_00:
            requires_approval = True
            reason += " Large exposure (>= ₹5 Lakhs) at Level 4+ requires supervisor review."
        elif relationship_tier == RelationshipTier.ENTERPRISE_VIP and next_level >= 4:
            requires_approval = True
            reason += " Enterprise VIP account escalation requires account executive review."

        return PolicyDecision(
            should_act=True,
            next_level=next_level,
            channel=channel,
            tone=tone,
            requires_human_approval=requires_approval,
            reason=reason,
        )
