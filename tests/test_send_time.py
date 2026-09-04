"""Unit tests for SendTimeOptimizer (Feature 5)."""

from datetime import datetime, timezone, timedelta
from src.engine.send_time import SendTimeOptimizer
from src.models.db_models import CommunicationChannel


def test_send_time_avoids_sunday():
    """If send time would fall on Sunday, it must shift to Monday."""
    # Create a Saturday night timestamp
    # 2026-09-05 is Saturday
    saturday_night = datetime(2026, 9, 5, 20, 0, 0, tzinfo=timezone.utc)
    optimal = SendTimeOptimizer.get_optimal_send_time(
        channel=CommunicationChannel.WHATSAPP,
        reference_time_utc=saturday_night,
    )
    # Check that optimal time is Monday (weekday == 0)
    # Convert to IST to verify business hour
    ist_time = optimal + timedelta(hours=5, minutes=30)
    assert ist_time.weekday() == 0  # Monday
    assert ist_time.hour == 10
    assert ist_time.minute == 30
