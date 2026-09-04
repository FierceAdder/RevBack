"""Feature 4: Multi-Channel Outreach and Fallback Cascade.

Coordinates communications across WhatsApp, Email, SMS, and Formal Notice
with intelligent fallback upon delivery failure or missing debtor contact info.
"""

from typing import Tuple, Optional, Dict, Any
from src.models.db_models import CommunicationChannel


class ChannelDispatcher:
    """Orchestrates communication channels and executes fallback logic."""

    @classmethod
    def resolve_channel(
        cls,
        target_channel: CommunicationChannel,
        has_email: bool,
        has_phone: bool,
    ) -> Tuple[CommunicationChannel, Optional[str]]:
        """
        Validates target channel against available debtor contact credentials
        and triggers graceful fallback if required.
        """
        if target_channel in (CommunicationChannel.WHATSAPP, CommunicationChannel.SMS):
            if not has_phone:
                if has_email:
                    return (
                        CommunicationChannel.EMAIL,
                        f"Target channel {target_channel.value} unavailable due to missing phone; gracefully fell back to EMAIL.",
                    )
                else:
                    return (
                        CommunicationChannel.FORMAL_NOTICE,
                        "Missing debtor phone and email; escalated to physical/formal notice dispatch.",
                    )

        if target_channel == CommunicationChannel.EMAIL and not has_email:
            if has_phone:
                return (
                    CommunicationChannel.WHATSAPP,
                    "Target channel EMAIL unavailable; gracefully fell back to WHATSAPP.",
                )
            else:
                return (
                    CommunicationChannel.FORMAL_NOTICE,
                    "Missing debtor contact information; routing to formal dispatch.",
                )

        return target_channel, None

    @classmethod
    def simulate_dispatch(
        cls,
        channel: CommunicationChannel,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simulates dispatch to messaging gateway (WhatsApp Business API / SendGrid / Twilio).
        """
        return {
            "channel": channel.value,
            "recipient": recipient,
            "subject": subject,
            "delivery_status": "DELIVERED",
            "gateway_message_id": f"msg_gw_{channel.value.lower()}_mock",
            "content_length": len(content),
        }
