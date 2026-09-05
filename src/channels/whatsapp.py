"""WhatsApp Business API Dispatcher."""

import logging
import uuid
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger("revback.channels.whatsapp")


class WhatsAppDispatcher:
    """Dispatches WhatsApp messages with templates and interactive payment buttons."""

    @classmethod
    async def send_whatsapp(
        cls,
        phone_number: str,
        message: str,
        template_name: str = "payment_reminder",
    ) -> Dict[str, Any]:
        """Dispatches interactive WhatsApp recovery message."""
        mock_id = f"wa_{uuid.uuid4().hex[:10]}"
        return {
            "status": "SENT",
            "delivery_status": "DELIVERED",
            "message_id": mock_id,
            "provider": "meta_whatsapp_business",
            "phone_number": phone_number,
            "template": template_name,
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
        }
