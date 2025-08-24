# 7_code_translation/src/deadline/world/character_manager.py
"""
Character management system - handles NPCs and their behaviors
"""
from typing import Any
from typing import Dict, List, Optional, Any
import logging
from ..core.game_object import Character, Room

logger = logging.getLogger(__name__)

class CharacterManager:
    """Manages all NPCs and their behaviors"""
    
    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.character_states: Dict[str, Dict[str, Any]] = {}
        
    def initialize(self, characters: Dict[str, Character]):
        """Initialize with character data"""
        self.characters = characters
        for char_id in characters:
            self.character_states[char_id] = {
                'current_schedule_index': 0,
                'last_update_time': 0,
                'mood': 'neutral',
                'suspicious': False
            }
    
    def update_all(self, current_time: int, rooms: Dict[str, Room]):
        """Update all characters based on current time"""
        for char_id, character in self.characters.items():
            self.update_character(char_id, current_time, rooms)
    
    def update_character(self, char_id: str, current_time: int, rooms: Dict[str, Room]):
        """Update a single character's position and activity"""
        if char_id not in self.characters:
            return
        
        character = self.characters[char_id]
        state = self.character_states[char_id]
        
        # Check schedule
        for schedule_item in character.schedule:
            if schedule_item.get('time') == current_time:
                # Move to scheduled location
                location = schedule_item.get('location')
                if location and location in rooms:
                    character.move_to(rooms[location])
                    logger.debug(f"{character.name} moved to {location}")
                
                # Update activity
                activity = schedule_item.get('activity')
                if activity:
                    character.update_activity(activity)
                    logger.debug(f"{character.name} is now {activity}")
        
        state['last_update_time'] = current_time
    
    def get_character_location(self, char_id: str) -> Optional[Room]:
        """Get the current location of a character"""
        if char_id in self.characters:
            char = self.characters[char_id]
            if isinstance(char.location, Room):
                return char.location
        return None
    
    def set_character_mood(self, char_id: str, mood: str):
        """Set a character's mood"""
        if char_id in self.character_states:
            self.character_states[char_id]['mood'] = mood
    
    def get_character_mood(self, char_id: str) -> str:
        """Get a character's current mood"""
        if char_id in self.character_states:
            return self.character_states[char_id].get('mood', 'neutral')
        return 'neutral'
    
    def make_suspicious(self, char_id: str):
        """Make a character suspicious"""
        if char_id in self.character_states:
            self.character_states[char_id]['suspicious'] = True
            self.set_character_mood(char_id, 'suspicious')
    
    def is_suspicious(self, char_id: str) -> bool:
        """Check if a character is suspicious"""
        if char_id in self.character_states:
            return self.character_states[char_id].get('suspicious', False)
        return False