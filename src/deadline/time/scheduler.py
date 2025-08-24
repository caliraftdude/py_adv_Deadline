# 7_code_translation/src/deadline/time/scheduler.py
"""
Event scheduling system
"""

from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
import heapq
from enum import Enum

from .events import EventType, GameEvent


@dataclass(order=True)
class ScheduledEvent:
    """A scheduled event with priority"""
    time: int
    event: GameEvent = field(compare=False)
    priority: int = 0
    
    def __lt__(self, other):
        if self.time != other.time:
            return self.time < other.time
        return self.priority < other.priority


class EventScheduler:
    """
    Manages scheduled events
    Uses a priority queue for efficient event processing
    """
    
    def __init__(self):
        self.events: List[ScheduledEvent] = []
        self.event_id_counter = 0
        self.cancelled_events: set = set()
    
    def schedule(self, event: GameEvent, priority: int = 0) -> int:
        """
        Schedule an event
        Returns event ID for cancellation
        """
        event_id = self.event_id_counter
        self.event_id_counter += 1
        
        scheduled = ScheduledEvent(
            time=event.time,
            event=event,
            priority=priority
        )
        
        heapq.heappush(self.events, scheduled)
        return event_id
    
    def get_events_at_time(self, time: int) -> List[GameEvent]:
        """Get all events scheduled for a specific time"""
        events = []
        
        # Look at events without removing them
        for scheduled in self.events:
            if scheduled.time == time:
                events.append(scheduled.event)
            elif scheduled.time > time:
                break  # Events are sorted by time
        
        return events
    
    def get_events_in_range(self, start_time: int, end_time: int) -> List[GameEvent]:
        """Get all events in a time range"""
        events = []
        processed = []
        
        while self.events:
            scheduled = heapq.heappop(self.events)
            
            if scheduled.time > end_time:
                # Put it back and stop
                heapq.heappush(self.events, scheduled)
                break
            
            if scheduled.time > start_time:
                events.append(scheduled.event)
            else:
                # Keep for later
                processed.append(scheduled)
        
        # Put back unprocessed events
        for scheduled in processed:
            heapq.heappush(self.events, scheduled)
        
        return events
    
    def cancel_events_of_type(self, event_type: EventType):
        """Cancel all events of a specific type"""
        remaining = []
        
        while self.events:
            scheduled = heapq.heappop(self.events)
            if scheduled.event.event_type != event_type:
                remaining.append(scheduled)
        
        # Rebuild heap
        self.events = remaining
        heapq.heapify(self.events)
    
    def clear_all_events(self):
        """Clear all scheduled events"""
        self.events.clear()
        self.cancelled_events.clear()
    
    def get_next_event_time(self) -> Optional[int]:
        """Get the time of the next scheduled event"""
        if self.events:
            return self.events[0].time
        return None
    
    def has_events(self) -> bool:
        """Check if there are any scheduled events"""
        return len(self.events) > 0
    
    def get_event_count(self) -> int:
        """Get number of scheduled events"""
        return len(self.events)
