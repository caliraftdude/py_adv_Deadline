# 7_code_translation/src/deadline/time/events.py
"""
Event definitions and types
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, Optional


class EventType(Enum):
    """Types of game events"""
    CHARACTER_MOVEMENT = auto()
    CHARACTER_ACTION = auto()
    DIALOGUE = auto()
    PHONE_CALL = auto()
    MEETING = auto()
    DISCOVERY = auto()
    TIME_LIMIT_WARNING = auto()
    GAME_OVER = auto()
    CUSTOM = auto()


@dataclass
class GameEvent:
    """A game event"""
    time: int
    event_type: EventType
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
    
    def get_character_id(self) -> Optional[str]:
        """Get character ID from event data"""
        return self.data.get('character_id')
    
    def get_location(self) -> Optional[str]:
        """Get location from event data"""
        return self.data.get('location')
    
    def get_action(self) -> Optional[str]:
        """Get action from event data"""
        return self.data.get('action')
    
    def get_message(self) -> Optional[str]:
        """Get message from event data"""
        return self.data.get('message')