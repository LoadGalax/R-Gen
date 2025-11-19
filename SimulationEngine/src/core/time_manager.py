"""
Time Management System for World Simulation

Handles time progression, scheduling, and temporal events.
"""

from datetime import datetime, timedelta
from typing import Optional, Callable, List, Dict
import json


class TimeManager:
    """
    Manages simulation time, day/night cycles, seasons, and time-based events.
    """

    # Time constants (minutes per period)
    MINUTES_PER_HOUR = 60
    HOURS_PER_DAY = 24
    DAYS_PER_MONTH = 30
    MONTHS_PER_YEAR = 12
    DAYS_PER_YEAR = 360  # Simplified calendar

    # Time periods
    TIME_PERIODS = {
        "night": (0, 6),      # 00:00 - 06:00
        "dawn": (6, 8),       # 06:00 - 08:00
        "morning": (8, 12),   # 08:00 - 12:00
        "afternoon": (12, 17),# 12:00 - 17:00
        "dusk": (17, 19),     # 17:00 - 19:00
        "evening": (19, 24),  # 19:00 - 00:00
    }

    SEASONS = ["Spring", "Summer", "Fall", "Winter"]

    def __init__(self, start_year: int = 1, start_day: int = 1, start_hour: int = 8):
        """
        Initialize the time manager.

        Args:
            start_year: Starting year
            start_day: Starting day of year (1-360)
            start_hour: Starting hour (0-23)
        """
        self.current_year = start_year
        self.current_day = start_day  # Day of year (1-360)
        self.current_hour = start_hour
        self.current_minute = 0

        # Total elapsed time in minutes
        self.total_minutes = 0

        # Scheduled events: {trigger_time: [callbacks]}
        self.scheduled_events: Dict[int, List[Callable]] = {}

        # Time scale (how many simulation minutes per real-time second)
        self.time_scale = 1.0

    @property
    def current_time_of_day(self) -> str:
        """Get current time period (night, dawn, morning, etc.)"""
        for period, (start, end) in self.TIME_PERIODS.items():
            if start <= self.current_hour < end:
                return period
        return "night"

    @property
    def current_season(self) -> str:
        """Get current season based on day of year"""
        day_in_season = self.current_day % 90
        season_index = (self.current_day - 1) // 90
        return self.SEASONS[season_index % 4]

    @property
    def current_month(self) -> int:
        """Get current month (1-12)"""
        return ((self.current_day - 1) // 30) + 1

    @property
    def day_of_month(self) -> int:
        """Get day of current month (1-30)"""
        return ((self.current_day - 1) % 30) + 1

    @property
    def is_daytime(self) -> bool:
        """Check if it's daytime (6:00 - 19:00)"""
        return 6 <= self.current_hour < 19

    @property
    def is_working_hours(self) -> bool:
        """Check if it's typical working hours (8:00 - 17:00)"""
        return 8 <= self.current_hour < 17

    def advance_minutes(self, minutes: int):
        """
        Advance time by specified minutes.

        Args:
            minutes: Number of minutes to advance
        """
        self.total_minutes += minutes
        self.current_minute += minutes

        # Handle minute overflow
        while self.current_minute >= self.MINUTES_PER_HOUR:
            self.current_minute -= self.MINUTES_PER_HOUR
            self.current_hour += 1

        # Handle hour overflow
        while self.current_hour >= self.HOURS_PER_DAY:
            self.current_hour -= self.HOURS_PER_DAY
            self.current_day += 1

        # Handle day overflow
        while self.current_day > self.DAYS_PER_YEAR:
            self.current_day -= self.DAYS_PER_YEAR
            self.current_year += 1

        # Process scheduled events
        self._process_scheduled_events()

    def advance_hours(self, hours: int):
        """Advance time by specified hours"""
        self.advance_minutes(hours * self.MINUTES_PER_HOUR)

    def advance_days(self, days: int):
        """Advance time by specified days"""
        self.advance_hours(days * self.HOURS_PER_DAY)

    def advance_to_time(self, hour: int, minute: int = 0):
        """
        Advance time to next occurrence of specified time.

        Args:
            hour: Target hour (0-23)
            minute: Target minute (0-59)
        """
        # Calculate minutes until target time
        target_minutes = (hour * 60) + minute
        current_minutes = (self.current_hour * 60) + self.current_minute

        if target_minutes > current_minutes:
            # Same day
            minutes_to_advance = target_minutes - current_minutes
        else:
            # Next day
            minutes_to_advance = (self.HOURS_PER_DAY * 60) - current_minutes + target_minutes

        self.advance_minutes(minutes_to_advance)

    def schedule_event(self, minutes_from_now: int, callback: Callable):
        """
        Schedule an event to occur after specified minutes.

        Args:
            minutes_from_now: Minutes until event triggers
            callback: Function to call when event triggers
        """
        trigger_time = self.total_minutes + minutes_from_now

        if trigger_time not in self.scheduled_events:
            self.scheduled_events[trigger_time] = []

        self.scheduled_events[trigger_time].append(callback)

    def _process_scheduled_events(self):
        """Process any events that should trigger at current time"""
        if self.total_minutes in self.scheduled_events:
            for callback in self.scheduled_events[self.total_minutes]:
                try:
                    callback()
                except Exception as e:
                    print(f"Error processing scheduled event: {e}")

            # Remove processed events
            del self.scheduled_events[self.total_minutes]

    def get_time_string(self) -> str:
        """Get formatted time string"""
        return f"{self.current_hour:02d}:{self.current_minute:02d}"

    def get_date_string(self) -> str:
        """Get formatted date string"""
        return f"Year {self.current_year}, Day {self.current_day}"

    def get_full_datetime_string(self) -> str:
        """Get full date and time string"""
        return (f"Year {self.current_year}, {self.current_season}, "
                f"Month {self.current_month}, Day {self.day_of_month} - "
                f"{self.get_time_string()} ({self.current_time_of_day})")

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "current_year": self.current_year,
            "current_day": self.current_day,
            "current_hour": self.current_hour,
            "current_minute": self.current_minute,
            "total_minutes": self.total_minutes,
            "time_scale": self.time_scale,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TimeManager':
        """Deserialize from dictionary"""
        tm = cls(
            start_year=data["current_year"],
            start_day=data["current_day"],
            start_hour=data["current_hour"]
        )
        tm.current_minute = data["current_minute"]
        tm.total_minutes = data["total_minutes"]
        tm.time_scale = data.get("time_scale", 1.0)
        return tm
