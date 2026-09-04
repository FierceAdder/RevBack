"""Feature 5: Optimal Send-Time Optimizer.

Schedules communications within legitimate business hours (IST)
and optimizes delivery based on debtor behavior and channel.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from src.models.db_models import CommunicationChannel


class SendTimeOptimizer:
    """Calculates optimal message dispatch timestamp."""

    # IST offset is UTC+5:30
    IST_OFFSET = timedelta(hours=5, minutes=30)
    
    # Business hours in IST (9:30 AM to 6:30 PM)
    START_HOUR_IST = 9
    START_MINUTE_IST = 30
    END_HOUR_IST = 18
    END_MINUTE_IST = 30

    @classmethod
    def get_optimal_send_time(
        cls,
        channel: CommunicationChannel,
        reference_time_utc: Optional[datetime] = None,
    ) -> datetime:
        """
        Calculates next optimal business window in UTC.
        Rules:
        - Never send on Sundays.
        - WhatsApp best time: 10:30 AM to 12:00 PM IST (high open rate).
        - Email best time: 10:00 AM to 11:30 AM IST or 2:30 PM to 4:00 PM IST.
        - Formal Notice: 11:00 AM IST.
        """
        now_utc = reference_time_utc or datetime.now(timezone.utc)
        ist_now = now_utc + cls.IST_OFFSET

        target_hour = 10
        target_minute = 30
        if channel == CommunicationChannel.EMAIL:
            target_hour = 10
            target_minute = 15
        elif channel == CommunicationChannel.FORMAL_NOTICE:
            target_hour = 11
            target_minute = 0

        # Construct target today in IST
        target_ist = ist_now.replace(
            hour=target_hour, minute=target_minute, second=0, microsecond=0
        )

        # If today's slot has passed or current time is past 18:30 IST, move to tomorrow
        if ist_now >= target_ist or ist_now.hour >= cls.END_HOUR_IST:
            target_ist += timedelta(days=1)

        # If target lands on Sunday (weekday == 6), move to Monday
        if target_ist.weekday() == 6:
            target_ist += timedelta(days=1)

        # Convert back to UTC
        optimal_utc = target_ist - cls.IST_OFFSET
        return optimal_utc
