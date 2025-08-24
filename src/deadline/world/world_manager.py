# 7_code_translation/src/deadline/world/world_manager.py
"""
World management system - manages all game objects, rooms, and characters
"""
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from ..parser.parser import ParseResult

from typing import Dict, List, Optional, Any, Set
import json
from pathlib import Path
import logging

from ..core.game_object import GameObject, Room, Item, Character, Player
from ..core.flags import ObjectFlag
from .room_manager import RoomManager
from .character_manager import CharacterManager
from .evidence_manager import EvidenceManager

logger = logging.getLogger(__name__)


class WorldManager:
    """
    Central manager for the game world
    Handles all objects, rooms, characters, and their interactions
    """
    
    def __init__(self, game_data: Dict[str, Any]):
        """Initialize world manager with game data"""
        self.game_data = game_data
        
        # Object registries
        self.objects: Dict[str, GameObject] = {}
        self.rooms: Dict[str, Room] = {}
        self.characters: Dict[str, Character] = {}
        
        # Player
        self.player: Optional[Player] = None
        
        # Subsystem managers
        self.room_manager = RoomManager()
        self.character_manager = CharacterManager()
        self.evidence_manager = EvidenceManager()
        
        # Current state
        self.current_room_id: Optional[str] = None
        
    def initialize_world(self):
        """Initialize the game world from data"""
        # Create player
        self._create_player()
        
        # Create rooms
        self._create_rooms()
        
        # Create objects
        self._create_objects()
        
        # Create characters
        self._create_characters()
        
        # Set initial positions
        self._set_initial_positions()
        
        # Initialize managers
        self.room_manager.initialize(self.rooms)
        self.character_manager.initialize(self.characters)
        self.evidence_manager.initialize(self.game_data.get('solution', {}))
        
        logger.info(f"World initialized with {len(self.rooms)} rooms, {len(self.objects)} objects, {len(self.characters)} characters")
    
    def _create_player(self):
        """Create the player character"""
        player_data = self.game_data.get('player', {})
        self.player = Player(
            max_carry_weight=player_data.get('max_carry_weight', 100),
            max_carry_items=player_data.get('max_carry_items', 10)
        )
        self.objects['player'] = self.player
        
        # Set starting room
        starting_room = player_data.get('starting_room', 'entrance_hall')
        self.current_room_id = starting_room
    
    def _create_rooms(self):
        """Create all rooms from game data"""
        rooms_data = self.game_data.get('rooms', {})
        
        for room_id, room_info in rooms_data.items():
            room = Room(
                id=room_id,
                name=room_info.get('name', 'Unknown Room'),
                description=room_info.get('description', ''),
                visited_description=room_info.get('visited_description', ''),
                exits=room_info.get('exits', {}),
                light_needed=room_info.get('light_needed', False)
            )
            
            # Set any special properties
            for prop, value in room_info.items():
                if prop not in ['name', 'description', 'visited_description', 'exits', 'light_needed', 'contents']:
                    room.set_property(prop, value)
            
            self.rooms[room_id] = room
            self.objects[room_id] = room
    
    def _create_objects(self):
        """Create all game objects from data"""
        objects_data = self.game_data.get('objects', {})
        
        for obj_id, obj_info in objects_data.items():
            # Parse flags
            flags = ObjectFlag.NONE
            for flag_name in obj_info.get('flags', []):
                try:
                    flags |= ObjectFlag[flag_name.upper()]
                except KeyError:
                    logger.warning(f"Unknown flag: {flag_name}")
            
            # Create appropriate object type
            if flags & ObjectFlag.CONTAINER:
                from ..core.game_object import Container
                obj = Container(
                    id=obj_id,
                    name=obj_info.get('name', 'unknown'),
                    description=obj_info.get('description', ''),
                    flags=flags,
                    capacity=obj_info.get('capacity', 10),
                    key_id=obj_info.get('key_id')
                )
            else:
                obj = Item(
                    id=obj_id,
                    name=obj_info.get('name', 'unknown'),
                    description=obj_info.get('description', ''),
                    flags=flags,
                    size=obj_info.get('size', 1),
                    weight=obj_info.get('weight', 1),
                    value=obj_info.get('value', 0)
                )
            
            # Set properties
            obj.synonyms = obj_info.get('synonyms', [])
            obj.adjectives = obj_info.get('adjectives', [])
            
            # Set custom properties
            for prop, value in obj_info.items():
                if prop not in ['name', 'description', 'flags', 'synonyms', 'adjectives', 
                               'size', 'weight', 'value', 'capacity', 'key_id', 'location', 'contents']:
                    obj.set_property(prop, value)
            
            self.objects[obj_id] = obj
    
    def _create_characters(self):
        """Create all NPCs from data"""
        characters_data = self.game_data.get('characters', {})
        
        for char_id, char_info in characters_data.items():
            character = Character(
                id=char_id,
                name=char_info.get('name', 'Unknown'),
                description=char_info.get('description', ''),
                knowledge=char_info.get('knowledge', {}),
                schedule=char_info.get('schedule', []),
                topics=char_info.get('conversation_topics', {}),
                trust_level=char_info.get('trust_level', 0)
            )
            
            character.synonyms = char_info.get('synonyms', [])
            
            # Set custom properties
            for prop, value in char_info.items():
                if prop not in ['name', 'description', 'knowledge', 'schedule', 
                               'conversation_topics', 'trust_level', 'synonyms', 'location']:
                    character.set_property(prop, value)
            
            self.characters[char_id] = character
            self.objects[char_id] = character
    
    def _set_initial_positions(self):
        """Set initial positions for objects and characters"""
        # Place player
        if self.current_room_id and self.current_room_id in self.rooms:
            self.player.move_to(self.rooms[self.current_room_id])
        
        # Place objects in rooms
        rooms_data = self.game_data.get('rooms', {})
        for room_id, room_info in rooms_data.items():
            if room_id in self.rooms:
                room = self.rooms[room_id]
                for obj_id in room_info.get('contents', []):
                    if obj_id in self.objects:
                        self.objects[obj_id].move_to(room)
        
        # Place objects in containers
        objects_data = self.game_data.get('objects', {})
        for obj_id, obj_info in objects_data.items():
            if 'contents' in obj_info and obj_id in self.objects:
                container = self.objects[obj_id]
                for content_id in obj_info['contents']:
                    if content_id in self.objects:
                        self.objects[content_id].move_to(container)
        
        # Place objects by location property
        for obj_id, obj_info in objects_data.items():
            if 'location' in obj_info and obj_id in self.objects:
                location_id = obj_info['location']
                if location_id in self.objects:
                    self.objects[obj_id].move_to(self.objects[location_id])
        
        # Place characters
        characters_data = self.game_data.get('characters', {})
        for char_id, char_info in characters_data.items():
            if 'location' in char_info and char_id in self.characters:
                location_id = char_info['location']
                if location_id in self.rooms:
                    self.characters[char_id].move_to(self.rooms[location_id])
    
    def get_current_room(self) -> Optional[Room]:
        """Get the room the player is currently in"""
        if self.player and self.player.location:
            return self.player.location if isinstance(self.player.location, Room) else None
        return None
    
    def move_player(self, direction: str) -> tuple[bool, str]:
        """
        Move player in a direction
        Returns (success, message)
        """
        current_room = self.get_current_room()
        if not current_room:
            return False, "You're not in a valid location."
        
        # Check if direction is valid
        new_room_id = current_room.get_exit(direction)
        if not new_room_id:
            return False, "You can't go that way."
        
        # Get new room
        if new_room_id not in self.rooms:
            return False, "That exit leads nowhere."
        
        new_room = self.rooms[new_room_id]
        
        # Check if room is accessible (could add locked doors, etc.)
        if new_room.is_dark() and not self.player_has_light():
            return False, "It's too dark to go that way."
        
        # Move player
        self.player.move_to(new_room)
        self.current_room_id = new_room_id
        
        # Mark room as visited
        new_room.set_flag(ObjectFlag.VISITED)
        
        return True, ""
    
    def player_has_light(self) -> bool:
        """Check if player has a light source"""
        for obj in self.player.contents:
            if obj.has_flag(ObjectFlag.LIGHT) and obj.has_flag(ObjectFlag.ON):
                return True
        return False
    
    def find_object(self, obj_ref: str) -> Optional[GameObject]:
        """
        Find an object by reference (ID or name)
        Searches in current room and player inventory
        """
        # Try direct ID lookup
        if obj_ref in self.objects:
            obj = self.objects[obj_ref]
            # Check if accessible
            current_room = self.get_current_room()
            if obj.location == self.player or obj.location == current_room:
                if obj.is_accessible():
                    return obj
        
        # Search by name in current room and inventory
        current_room = self.get_current_room()
        if current_room:
            # Search room contents
            for obj in current_room.contents:
                if obj.name.lower() == obj_ref.lower():
                    if obj.is_accessible():
                        return obj
                # Check synonyms
                for synonym in obj.synonyms:
                    if synonym.lower() == obj_ref.lower():
                        if obj.is_accessible():
                            return obj
        
        # Search player inventory
        for obj in self.player.contents:
            if obj.name.lower() == obj_ref.lower():
                return obj
            # Check synonyms
            for synonym in obj.synonyms:
                if synonym.lower() == obj_ref.lower():
                    return obj
        
        return None
    
    def get_visible_objects(self) -> List[GameObject]:
        """Get all objects visible to the player"""
        visible = []
        current_room = self.get_current_room()
        
        if current_room:
            # Add room contents
            for obj in current_room.contents:
                if obj.is_visible() and obj != self.player:
                    visible.append(obj)
                    # Add contents of open/transparent containers
                    if obj.has_flag(ObjectFlag.CONTAINER):
                        if obj.has_flag(ObjectFlag.OPEN) or obj.has_flag(ObjectFlag.TRANSPARENT):
                            for inner_obj in obj.contents:
                                if inner_obj.is_visible():
                                    visible.append(inner_obj)
        
        # Add player inventory
        visible.extend(self.player.contents)
        
        return visible
    
    def update_characters(self, current_time: int):
        """Update all character positions and activities based on time"""
        self.character_manager.update_all(current_time, self.rooms)
    
    def move_character(self, char_id: str, room_id: str):
        """Move a character to a new room"""
        if char_id in self.characters and room_id in self.rooms:
            self.characters[char_id].move_to(self.rooms[room_id])
    
    def character_action(self, char_id: str, action: str):
        """Perform a character action"""
        if char_id in self.characters:
            self.characters[char_id].update_activity(action)