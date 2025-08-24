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
        """Create the player character from data"""
        player_data = self.game_data.get('player', {})
        
        if not player_data:
            logger.warning("No player data found, using defaults")
            player_data = {
                'name': 'Detective',
                'description': 'You are a police detective investigating the Robner case.'
            }
        
        # Import the factory function
        from ..core.game_object import create_game_object_from_data, Player
        
        try:
            # Ensure type is set to 'player' for the factory
            player_data['type'] = 'player'
            
            # Create player using factory
            self.player = create_game_object_from_data('player', player_data)
            
            # Verify it's actually a Player object
            if not isinstance(self.player, Player):
                # If factory didn't create a Player, create one directly
                logger.warning("Factory didn't create Player object, creating directly")
                self.player = Player(
                    id='player',
                    name=player_data.get('name', 'Detective'),
                    description=player_data.get('description', 'You are a detective.'),
                    max_carry=player_data.get('max_carry', 10)
                )
            
            # Set starting location
            starting_room = player_data.get('starting_room', list(self.rooms.keys())[0] if self.rooms else None)
            if starting_room and starting_room in self.rooms:
                self.player.location = self.rooms[starting_room]
                self.current_room_id = starting_room
                logger.debug(f"Player starting in room: {starting_room}")
            else:
                logger.warning(f"Invalid starting room: {starting_room}")
            
            # Set starting inventory
            starting_inventory = player_data.get('starting_inventory', [])
            for item_id in starting_inventory:
                if item_id in self.objects:
                    self.player.add_to_inventory(self.objects[item_id])
                    logger.debug(f"Added {item_id} to player inventory")
            
            logger.info("Created player character")
            
        except Exception as e:
            logger.error(f"Failed to create player: {e}")
            # Create a default player as fallback
            self.player = Player(
                id='player',
                name='Detective',
                description='You are a detective.'
            )
    
    def _create_rooms(self):
        """Create all rooms from data"""
        rooms_data = self.game_data.get('rooms', {})
        
        # Import the factory function
        from ..core.game_object import create_game_object_from_data, Room
        
        for room_id, room_info in rooms_data.items():
            try:
                # Ensure type is set to 'room' for the factory
                room_info['type'] = 'room'
                
                # Use the factory function
                room = create_game_object_from_data(room_id, room_info)
                
                # Verify it's actually a Room object
                if not isinstance(room, Room):
                    logger.error(f"Failed to create room {room_id}: factory returned {type(room).__name__}")
                    continue
                
                # Register in rooms dictionary
                self.rooms[room_id] = room
                
                # Also register in the main objects dictionary for consistency
                self.objects[room_id] = room
                
                # Store initial contents if specified
                if 'contents' in room_info:
                    room.initial_contents = room_info.get('contents', [])
                
                # Register with room manager
                self.room_manager.register_room(room)
                
                logger.debug(f"Created room: {room_id}")
                
            except Exception as e:
                logger.error(f"Failed to create room {room_id}: {e}")
                continue
    
    logger.info(f"Created {len(self.rooms)} rooms")
    
    def _create_objects(self):
        """Create all game objects from data"""
        objects_data = self.game_data.get('objects', {})
        
        # Import the factory function
        from ..core.game_object import create_game_object_from_data
        
        for obj_id, obj_info in objects_data.items():
            try:
                # Use the factory function to create the appropriate object type
                obj = create_game_object_from_data(obj_id, obj_info)
                
                # Register the object in the main objects dictionary
                self.objects[obj_id] = obj
                
                # Store initial location and contents for later setup by _set_initial_positions()
                if 'location' in obj_info:
                    obj.initial_location = obj_info['location']
                
                if 'contents' in obj_info:
                    obj.initial_contents = obj_info.get('contents', [])
                
                logger.debug(f"Created object: {obj_id} ({type(obj).__name__})")
                
            except Exception as e:
                logger.error(f"Failed to create object {obj_id}: {e}")
                # Continue loading other objects even if one fails
                continue
        
        logger.info(f"Created {len(self.objects)} objects")
    
    def _create_characters(self):
        """Create all characters from data"""
        characters_data = self.game_data.get('characters', {})
        
        # Import the factory function
        from ..core.game_object import create_game_object_from_data, Character
        
        for char_id, char_info in characters_data.items():
            try:
                # Ensure type is set for the factory
                char_info['type'] = 'character'
                
                # Use the factory function
                character = create_game_object_from_data(char_id, char_info)
                
                # Verify it's actually a Character object
                if not isinstance(character, Character):
                    logger.error(f"Failed to create character {char_id}: factory returned {type(character).__name__}")
                    continue
                
                # Register in characters dictionary
                self.characters[char_id] = character
                
                # Also register in the main objects dictionary
                self.objects[char_id] = character
                
                # Store initial location if specified
                if 'location' in char_info:
                    character.initial_location = char_info['location']
                
                # Register with character manager
                self.character_manager.register_character(character)
                
                logger.debug(f"Created character: {char_id}")
                
            except Exception as e:
                logger.error(f"Failed to create character {char_id}: {e}")
                continue
        
        logger.info(f"Created {len(self.characters)} characters")
    
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