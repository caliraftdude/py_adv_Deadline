# 7_code_translation/src/deadline/time/time_manager.py
"""
Time management system - handles game time and scheduling
Translated from ZIL's CLOCK and daemon system
"""

from typing import Dict, List, Optional, Callable, Any
import json
from pathlib import Path
import logging
from dataclasses import dataclass
import heapq

from .scheduler import EventScheduler, ScheduledEvent
from .events import EventType, GameEvent

logger = logging.getLogger(__name__)


class TimeManager:
    """
    Manages game time and scheduled events
    Equivalent to ZIL's CLOCK-DAEMON and event system
    """
    
    def __init__(self, start_time: int = 480):  # 8:00 AM default
        """
        Initialize time manager
        
        Args:
            start_time: Starting time in minutes since midnight
        """
        self.current_time = start_time
        self.scheduler = EventScheduler()
        self.daemons: Dict[str, Callable] = {}  # Recurring events
        self.time_stopped = False
        
        # Time formatting
        self.day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.current_day = 5  # Saturday (matching original game)
        
    def load_schedules(self, schedule_file: Path):
        """Load scheduled events from JSON file"""
        try:
            with open(schedule_file, 'r') as f:
                schedules_data = json.load(f)
            
            # Load one-time events
            for event_data in schedules_data.get('events', []):
                event = GameEvent(
                    time=event_data['time'],
                    event_type=EventType[event_data['type']],
                    data=event_data.get('data', {})
                )
                self.scheduler.schedule(event)
            
            # Load recurring events (daemons)
            for daemon_data in schedules_data.get('daemons', []):
                # These would be function references in actual implementation
                pass
            
            logger.info(f"Loaded {len(schedules_data.get('events', []))} scheduled events")
            
        except Exception as e:
            logger.error(f"Failed to load schedules: {e}")
    
    def advance_time(self, minutes: int = 1):
        """
        Advance game time by specified minutes
        Processes any events that occur
        """
        if self.time_stopped:
            return
        
        old_time = self.current_time
        self.current_time += minutes
        
        # Check for day rollover
        if self.current_time >= 1440:  # 24 hours * 60 minutes
            self.current_time %= 1440
            self.current_day = (self.current_day + 1) % 7
        
        # Process events in the time range
        events = self.scheduler.get_events_in_range(old_time, self.current_time)
        for event in events:
            self._process_event(event)
        
        # Run daemons
        for daemon_name, daemon_func in self.daemons.items():
            try:
                daemon_func()
            except Exception as e:
                logger.error(f"Daemon {daemon_name} error: {e}")
    
    def get_current_events(self) -> List[GameEvent]:
        """Get events scheduled for current time"""
        return self.scheduler.get_events_at_time(self.current_time)
    
    def schedule_event(self, delay: int, event_type: EventType, data: Dict[str, Any] = None):
        """
        Schedule an event to occur after a delay
        Equivalent to ZIL's QUEUE/FUSE
        """
        event = GameEvent(
            time=self.current_time + delay,
            event_type=event_type,
            data=data or {}
        )
        self.scheduler.schedule(event)
    
    def cancel_event(self, event_type: EventType):
        """
        Cancel scheduled events of a specific type
        Equivalent to ZIL's DEQUEUE
        """
        self.scheduler.cancel_events_of_type(event_type)
    
    def register_daemon(self, name: str, callback: Callable):
        """
        Register a recurring event
        Equivalent to ZIL's DAEMON
        """
        self.daemons[name] = callback
    
    def unregister_daemon(self, name: str):
        """
        Remove a recurring event
        Equivalent to ZIL's DISABLE
        """
        if name in self.daemons:
            del self.daemons[name]
    
    def stop_time(self):
        """Stop time advancement"""
        self.time_stopped = True
    
    def start_time(self):
        """Resume time advancement"""
        self.time_stopped = False
    
    def get_time_string(self) -> str:
        """Get formatted time string (e.g., '9:30 AM')"""
        hours = self.current_time // 60
        minutes = self.current_time % 60
        
        period = "AM" if hours < 12 else "PM"
        display_hours = hours if hours <= 12 else hours - 12
        if display_hours == 0:
            display_hours = 12
        
        return f"{display_hours}:{minutes:02d} {period}"
    
    def get_day_string(self) -> str:
        """Get current day name"""
        return self.day_names[self.current_day]
    
    def get_full_time_string(self) -> str:
        """Get full time and day string"""
        return f"{self.get_day_string()}, {self.get_time_string()}"
    
    def is_business_hours(self) -> bool:
        """Check if current time is during business hours"""
        return 540 <= self.current_time < 1020  # 9 AM to 5 PM
    
    def is_night(self) -> bool:
        """Check if it's nighttime"""
        return self.current_time < 360 or self.current_time >= 1200  # Before 6 AM or after 8 PM
    
    def wait_until(self, target_time: int) -> int:
        """
        Wait until a specific time
        Returns number of minutes waited
        """
        if target_time <= self.current_time:
            # Target is tomorrow
            minutes_to_wait = (1440 - self.current_time) + target_time
        else:
            minutes_to_wait = target_time - self.current_time
        
        self.advance_time(minutes_to_wait)
        return minutes_to_wait
    
    def wait_for_duration(self, minutes: int):
        """Wait for a specific duration"""
        self.advance_time(minutes)
    
    def _process_event(self, event: GameEvent):
        """Process a single event"""
        logger.debug(f"Processing event: {event.event_type} at time {self.current_time}")
        # Event processing would be handled by game engine
        pass