# 7_code_translation/src/deadline/core/game_object.py
"""
Base game object classes - translated from ZIL object system
Implements the core object hierarchy and property system
"""

from typing import Dict, List, Any, Optional, Set, TYPE_CHECKING, Tuple
from dataclasses import dataclass, field
from enum import Flag, auto
import logging

from .flags import ObjectFlag

if TYPE_CHECKING:
    from .property_system import PropertyManager

logger = logging.getLogger(__name__)


@dataclass
class GameObject:
    """
    Base class for all game objects
    Equivalent to ZIL OBJECT definition
    """
    
    # Core properties - match ZIL object properties
    id: str                                    # Unique identifier
    name: str                                  # Short name (DESC in ZIL)
    description: str = ""                      # Long description (LDESC)
    initial_description: str = ""              # First-time description (FDESC)
    flags: ObjectFlag = ObjectFlag.NONE        # Object flags
    
    # Containment hierarchy - ZIL's IN/LOC system
    location: Optional['GameObject'] = None    # Where this object is (LOC)
    contents: List['GameObject'] = field(default_factory=list)  # What's inside
    
    # Properties dictionary - ZIL's property system
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Vocabulary - for parser matching
    synonyms: List[str] = field(default_factory=list)    # Alternative names
    adjectives: List[str] = field(default_factory=list)  # Descriptive words
    
    # Action handler - equivalent to ZIL's ACTION property
    action_handler: Optional[str] = None       # Name of action routine
    
    # State tracking
    _original_location: Optional['GameObject'] = None
    _state_variables: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize object after creation"""
        # Store original location for reset
        self._original_location = self.location
        
        # Add self to location's contents if location exists
        if self.location:
            self.move_to(self.location)
    
    def has_flag(self, flag: ObjectFlag) -> bool:
        """
        Check if object has a specific flag
        Equivalent to ZIL's FSET?
        """
        return bool(self.flags & flag)
    
    def set_flag(self, flag: ObjectFlag):
        """
        Set a flag on the object
        Equivalent to ZIL's FSET
        """
        self.flags |= flag
    
    def clear_flag(self, flag: ObjectFlag):
        """
        Clear a flag from the object
        Equivalent to ZIL's FCLEAR
        """
        self.flags &= ~flag
    
    def toggle_flag(self, flag: ObjectFlag):
        """Toggle a flag"""
        self.flags ^= flag
    
    def get_property(self, prop_name: str, default: Any = None) -> Any:
        """
        Get a property value
        Equivalent to ZIL's GETP
        """
        return self.properties.get(prop_name, default)
    
    def set_property(self, prop_name: str, value: Any):
        """
        Set a property value
        Equivalent to ZIL's PUTP
        """
        self.properties[prop_name] = value
    
    def has_property(self, prop_name: str) -> bool:
        """Check if object has a property"""
        return prop_name in self.properties
    
    def move_to(self, new_location: Optional['GameObject']):
        """
        Move object to a new location
        Equivalent to ZIL's MOVE
        """
        # Remove from current location
        if self.location and self in self.location.contents:
            self.location.contents.remove(self)
        
        # Set new location
        self.location = new_location
        
        # Add to new location's contents
        if new_location and self not in new_location.contents:
            new_location.contents.append(self)
    
    def is_in(self, container: 'GameObject') -> bool:
        """
        Check if object is in a specific container (recursively)
        Equivalent to ZIL's IN?
        """
        current = self.location
        while current:
            if current == container:
                return True
            current = current.location
        return False
    
    def is_accessible(self) -> bool:
        """
        Check if object is accessible to player
        Considers containers being open, etc.
        """
        # Check if any parent container is closed
        current = self.location
        while current:
            if current.has_flag(ObjectFlag.CONTAINER):
                if not current.has_flag(ObjectFlag.OPEN):
                    return False
            current = current.location
        return True
    
    def is_visible(self) -> bool:
        """Check if object is visible to player"""
        if self.has_flag(ObjectFlag.INVISIBLE):
            return False
        
        # Check if in a transparent or open container
        if self.location and self.location.has_flag(ObjectFlag.CONTAINER):
            if not (self.location.has_flag(ObjectFlag.OPEN) or 
                   self.location.has_flag(ObjectFlag.TRANSPARENT)):
                return False
        
        return True
    
    def get_all_contents(self, recursive: bool = True) -> List['GameObject']:
        """
        Get all contents, optionally recursive
        Equivalent to ZIL's FIRST?/NEXT? iteration
        """
        result = list(self.contents)
        
        if recursive:
            for obj in self.contents:
                result.extend(obj.get_all_contents(recursive=True))
        
        return result
    
    def find_object(self, obj_id: str) -> Optional['GameObject']:
        """Find an object by ID in contents (recursive)"""
        for obj in self.contents:
            if obj.id == obj_id:
                return obj
            found = obj.find_object(obj_id)
            if found:
                return found
        return None
    
    def matches_vocabulary(self, words: List[str]) -> bool:
        """
        Check if object matches given vocabulary words
        Used by parser for object identification
        """
        # Check if any word matches name or synonyms
        obj_words = [self.name.lower()] + [s.lower() for s in self.synonyms]
        
        for word in words:
            word_lower = word.lower()
            if word_lower in obj_words:
                return True
            
            # Check adjectives
            if word_lower in [adj.lower() for adj in self.adjectives]:
                # Adjective alone doesn't match, need noun too
                continue
        
        return False
    
    def get_description(self, detailed: bool = False) -> str:
        """
        Get object description
        Returns initial description on first view, then regular description
        """
        # Check for initial description
        if self.initial_description and not self.has_flag(ObjectFlag.VISITED):
            self.set_flag(ObjectFlag.VISITED)
            return self.initial_description
        
        # Return regular description
        if detailed and self.description:
            return self.description
        
        return f"You see {self.get_article()} {self.name} here."
    
    def get_article(self) -> str:
        """Get appropriate article for object"""
        if self.has_flag(ObjectFlag.PROPER) or self.has_flag(ObjectFlag.NARTICLE):
            return ""
        if self.has_flag(ObjectFlag.PLURAL):
            return "some"
        
        # Check for vowel start
        if self.name and self.name[0].lower() in 'aeiou':
            return "an"
        return "a"
    
    def get_inventory_description(self) -> str:
        """Get description for inventory listing"""
        article = self.get_article()
        if article:
            return f"{article} {self.name}"
        return self.name
    
    def can_take(self) -> bool:
        """Check if object can be taken"""
        return self.has_flag(ObjectFlag.TAKEABLE) and not self.has_flag(ObjectFlag.SACRED)
    
    def can_contain(self, obj: 'GameObject') -> bool:
        """
        Check if this object can contain another object
        Considers capacity, size, etc.
        """
        if not self.has_flag(ObjectFlag.CONTAINER) and not self.has_flag(ObjectFlag.SURFACE):
            return False
        
        # Check capacity if defined
        capacity = self.get_property('capacity', float('inf'))
        if len(self.contents) >= capacity:
            return False
        
        # Check size constraints if defined
        max_size = self.get_property('max_item_size')
        if max_size and obj.get_property('size', 0) > max_size:
            return False
        
        return True
    
    def reset(self):
        """Reset object to initial state"""
        self.move_to(self._original_location)
        self.flags = ObjectFlag.NONE  # Reset to initial flags
        self._state_variables.clear()
    
    def save_state(self) -> Dict[str, Any]:
        """Save object state for game saves"""
        return {
            'id': self.id,
            'location': self.location.id if self.location else None,
            'flags': self.flags.value,
            'properties': dict(self.properties),
            'state_variables': dict(self._state_variables)
        }
    
    def load_state(self, state: Dict[str, Any]):
        """Load object state from save data"""
        self.flags = ObjectFlag(state.get('flags', 0))
        self.properties.update(state.get('properties', {}))
        self._state_variables.update(state.get('state_variables', {}))
        # Location will be restored by world manager
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"GameObject(id='{self.id}', name='{self.name}', location={self.location.id if self.location else None})"


class Room(GameObject):
    """
    Room class - represents locations in the game
    Equivalent to ZIL rooms with special properties
    """
    
    def __init__(self, **kwargs):
        # Rooms typically have these flags
        kwargs.setdefault('flags', ObjectFlag.NONE)
        super().__init__(**kwargs)
        
        # Room-specific properties
        self.exits: Dict[str, str] = kwargs.get('exits', {})  # direction -> room_id
        self.light_needed: bool = kwargs.get('light_needed', False)
        self.visited_description: str = kwargs.get('visited_description', "")
        
    def get_exit(self, direction: str) -> Optional[str]:
        """Get room ID for exit in given direction"""
        return self.exits.get(direction.lower())
    
    def add_exit(self, direction: str, room_id: str):
        """Add an exit to this room"""
        self.exits[direction.lower()] = room_id
    
    def remove_exit(self, direction: str):
        """Remove an exit from this room"""
        self.exits.pop(direction.lower(), None)
    
    def get_available_exits(self) -> List[str]:
        """Get list of available exit directions"""
        return list(self.exits.keys())
    
    def is_dark(self) -> bool:
        """Check if room is dark (needs light)"""
        if not self.light_needed:
            return False
        
        # Check for light sources in room
        for obj in self.get_all_contents():
            if obj.has_flag(ObjectFlag.LIGHT) and obj.has_flag(ObjectFlag.ON):
                return False
        
        return True
    
    def get_room_description(self) -> str:
        """Get appropriate room description"""
        if self.has_flag(ObjectFlag.VISITED) and self.visited_description:
            return self.visited_description
        return self.description

    # Add this method to the Room class in game_object.py

    def update_contents_cache(self):
        """
        Update cached list of visible contents in this room.
        This improves performance for frequently accessed room contents.
        """
        # This is just a helper to ensure the contents list is current
        # The actual contents are managed by the base GameObject class
        
        # Optional: Create a cached list of immediately visible objects
        # (not including contents of closed containers)
        visible_contents = []
        
        for obj in self.contents:
            visible_contents.append(obj)
            
            # Add contents of open/transparent containers
            if obj.has_flag(ObjectFlag.CONTAINER):
                if obj.has_flag(ObjectFlag.OPEN) or obj.has_flag(ObjectFlag.TRANSPARENT):
                    # Add visible contents of open containers
                    for inner_obj in obj.contents:
                        if not inner_obj.has_flag(ObjectFlag.HIDDEN):
                            visible_contents.append(inner_obj)
        
        # Store as a cached property
        self._visible_contents_cache = visible_contents
        
        return visible_contents

class Item(GameObject):
    """
    Item class - represents takeable objects
    Equivalent to ZIL objects with TAKEBIT
    """
    
    def __init__(self, **kwargs):
        kwargs.setdefault('flags', ObjectFlag.TAKEABLE)
        super().__init__(**kwargs)
        
        # Item-specific properties
        self.size: int = kwargs.get('size', 1)
        self.weight: int = kwargs.get('weight', 1)
        self.value: int = kwargs.get('value', 0)


class Container(GameObject):
    """
    Container class - can hold other objects
    Equivalent to ZIL objects with CONTBIT
    """
    
    def __init__(self, **kwargs):
        flags = kwargs.get('flags', ObjectFlag.NONE)
        kwargs['flags'] = flags | ObjectFlag.CONTAINER
        super().__init__(**kwargs)
        
        # Container-specific properties
        self.capacity: int = kwargs.get('capacity', 10)
        self.key_id: Optional[str] = kwargs.get('key_id')  # ID of key that opens this
        
    def open(self) -> bool:
        """Open the container"""
        if self.has_flag(ObjectFlag.LOCKED):
            return False
        self.set_flag(ObjectFlag.OPEN)
        return True
    
    def close(self) -> bool:
        """Close the container"""
        self.clear_flag(ObjectFlag.OPEN)
        return True
    
    def lock(self, key: Optional['GameObject'] = None) -> bool:
        """Lock the container"""
        if not self.has_flag(ObjectFlag.OPEN):
            if not key or key.id == self.key_id:
                self.set_flag(ObjectFlag.LOCKED)
                return True
        return False
    
    def unlock(self, key: Optional['GameObject'] = None) -> bool:
        """Unlock the container"""
        if key and key.id == self.key_id:
            self.clear_flag(ObjectFlag.LOCKED)
            return True
        return False


class Character(GameObject):
    """
    Character class - represents NPCs
    Equivalent to ZIL person objects with PERSONBIT
    """
    
    def __init__(self, **kwargs):
        flags = kwargs.get('flags', ObjectFlag.NONE)
        kwargs['flags'] = flags | ObjectFlag.PERSON
        super().__init__(**kwargs)
        
        # Character-specific properties
        self.dialogue_state: Dict[str, Any] = {}
        self.knowledge: Dict[str, Any] = kwargs.get('knowledge', {})
        self.schedule: List[Dict] = kwargs.get('schedule', [])
        self.current_activity: Optional[str] = None
        self.conversation_topics: Dict[str, str] = kwargs.get('topics', {})
        self.trust_level: int = kwargs.get('trust_level', 0)
        
    def get_response(self, topic: str) -> str:
        """Get character's response to a topic"""
        # Check if character has specific response
        if topic in self.conversation_topics:
            return self.conversation_topics[topic]
        
        # Check knowledge base
        if topic in self.knowledge:
            return self.knowledge[topic]
        
        # Default response
        return f"{self.name} doesn't seem to know about that."
    
    def update_activity(self, activity: str):
        """Update character's current activity"""
        self.current_activity = activity
    
    def can_see_player(self, player_location: 'Room') -> bool:
        """Check if character can see the player"""
        return self.location == player_location
    
    def react_to_action(self, action: str, obj: Optional['GameObject'] = None) -> Optional[str]:
        """React to player's action if visible"""
        # This would contain character-specific reactions
        reactions = self.get_property('reactions', {})
        return reactions.get(action)


class Player(GameObject):
    """
    Player class - represents the player character
    Special handling for inventory and state
    """
    
    def __init__(self, **kwargs):
        kwargs['id'] = 'player'
        kwargs['name'] = 'yourself'
        kwargs.setdefault('flags', ObjectFlag.PERSON)
        super().__init__(**kwargs)
        
        # Player-specific properties
        self.max_carry_weight: int = kwargs.get('max_carry_weight', 100)
        self.max_carry_items: int = kwargs.get('max_carry_items', 10)
        
    def can_carry(self, obj: GameObject) -> bool:
        """Check if player can carry an object"""
        if not obj.can_take():
            return False
        
        # Check item count
        carried_items = [o for o in self.contents if o.has_flag(ObjectFlag.TAKEABLE)]
        if len(carried_items) >= self.max_carry_items:
            return False
        
        # Check weight if applicable
        if hasattr(obj, 'weight'):
            total_weight = sum(getattr(o, 'weight', 0) for o in carried_items)
            if total_weight + obj.weight > self.max_carry_weight:
                return False
        
        return True
    
    def get_inventory(self) -> List[GameObject]:
        """Get list of carried items"""
        return [obj for obj in self.contents if obj.has_flag(ObjectFlag.TAKEABLE)]
    
    def is_wearing(self, obj: GameObject) -> bool:
        """Check if player is wearing an object"""
        return obj in self.contents and obj.has_flag(ObjectFlag.WEARABLE) and obj.get_property('worn', False)


class Door(GameObject):
    """
    Door class - represents connections between rooms
    Can be locked, opened, closed
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Door-specific properties
        self.connects: Tuple[str, str] = kwargs.get('connects', (None, None))
        self.key_id: Optional[str] = kwargs.get('key_id')
        self.both_sides: bool = kwargs.get('both_sides', True)  # Visible from both sides
        
        # Doors typically start closed
        if 'flags' not in kwargs:
            self.flags = ObjectFlag.NONE
    
    def is_passable(self) -> bool:
        """Check if door can be passed through"""
        return self.has_flag(ObjectFlag.OPEN) or not self.has_flag(ObjectFlag.LOCKED)
    
    def open(self) -> bool:
        """Open the door"""
        if self.has_flag(ObjectFlag.LOCKED):
            return False
        self.set_flag(ObjectFlag.OPEN)
        return True
    
    def close(self) -> bool:
        """Close the door"""
        self.clear_flag(ObjectFlag.OPEN)
        return True
    
    def lock(self, key: Optional['GameObject'] = None) -> bool:
        """Lock the door"""
        if self.has_flag(ObjectFlag.OPEN):
            return False  # Can't lock an open door
        
        if self.key_id and (not key or key.id != self.key_id):
            return False  # Wrong key or no key when required
        
        self.set_flag(ObjectFlag.LOCKED)
        return True
    
    def unlock(self, key: Optional['GameObject'] = None) -> bool:
        """Unlock the door"""
        if not self.has_flag(ObjectFlag.LOCKED):
            return True  # Already unlocked
        
        if self.key_id and (not key or key.id != self.key_id):
            return False  # Wrong key or no key when required
        
        self.clear_flag(ObjectFlag.LOCKED)
        return True
    
    def get_other_side(self, current_room: str) -> Optional[str]:
        """Get the room on the other side of the door"""
        if current_room == self.connects[0]:
            return self.connects[1]
        elif current_room == self.connects[1]:
            return self.connects[0]
        return None


class Evidence(GameObject):
    """
    Evidence class - special items that contribute to solving the murder
    """
    
    def __init__(self, **kwargs):
        kwargs.setdefault('flags', ObjectFlag.TAKEABLE | ObjectFlag.READABLE)
        super().__init__(**kwargs)
        
        # Evidence-specific properties
        self.evidence_value: int = kwargs.get('evidence_value', 5)
        self.reveals: List[str] = kwargs.get('reveals', [])  # What facts this reveals
        self.contradicts: List[str] = kwargs.get('contradicts', [])  # What claims this contradicts
        self.required_for_solution: bool = kwargs.get('required_for_solution', False)
        self.examined: bool = False
        
    def examine(self) -> str:
        """Examine the evidence"""
        self.examined = True
        self.set_flag(ObjectFlag.VISITED)
        
        # Return special examination text if available
        exam_text = self.get_property('examination_text')
        if exam_text:
            return exam_text
        
        return self.description
    
    def is_critical(self) -> bool:
        """Check if this evidence is critical to solving the case"""
        return self.required_for_solution
    
    def get_implications(self) -> List[str]:
        """Get what this evidence implies about the case"""
        implications = []
        
        if self.reveals:
            implications.extend([f"This reveals: {fact}" for fact in self.reveals])
        
        if self.contradicts:
            implications.extend([f"This contradicts: {claim}" for claim in self.contradicts])
        
        return implications


class Weapon(GameObject):
    """
    Weapon class - objects that can be used as weapons
    """
    
    def __init__(self, **kwargs):
        flags = kwargs.get('flags', ObjectFlag.NONE)
        kwargs['flags'] = flags | ObjectFlag.WEAPON | ObjectFlag.TAKEABLE
        super().__init__(**kwargs)
        
        # Weapon-specific properties
        self.damage: int = kwargs.get('damage', 1)
        self.used_in_crime: bool = kwargs.get('used_in_crime', False)
        self.fingerprints: List[str] = kwargs.get('fingerprints', [])
    
    def has_fingerprints_of(self, character_id: str) -> bool:
        """Check if weapon has specific character's fingerprints"""
        return character_id in self.fingerprints
    
    def add_fingerprints(self, character_id: str):
        """Add fingerprints to the weapon"""
        if character_id not in self.fingerprints:
            self.fingerprints.append(character_id)


class Document(GameObject):
    """
    Document class - readable objects with text content
    """
    
    def __init__(self, **kwargs):
        flags = kwargs.get('flags', ObjectFlag.NONE)
        kwargs['flags'] = flags | ObjectFlag.READABLE
        if kwargs.get('takeable', True):
            kwargs['flags'] |= ObjectFlag.TAKEABLE
        super().__init__(**kwargs)
        
        # Document-specific properties
        self.text_content: str = kwargs.get('text_content', "")
        self.pages: List[str] = kwargs.get('pages', [])
        self.current_page: int = 0
        self.signature: Optional[str] = kwargs.get('signature')
        self.date: Optional[str] = kwargs.get('date')
    
    def read(self, page: Optional[int] = None) -> str:
        """Read the document"""
        self.set_flag(ObjectFlag.VISITED)
        
        if self.pages:
            if page is not None and 0 <= page < len(self.pages):
                return self.pages[page]
            elif self.current_page < len(self.pages):
                return self.pages[self.current_page]
        
        if self.text_content:
            result = self.text_content
            if self.signature:
                result += f"\n\nSigned: {self.signature}"
            if self.date:
                result += f"\nDated: {self.date}"
            return result
        
        return "The document is blank."
    
    def turn_page(self, forward: bool = True) -> bool:
        """Turn to next/previous page"""
        if not self.pages:
            return False
        
        if forward and self.current_page < len(self.pages) - 1:
            self.current_page += 1
            return True
        elif not forward and self.current_page > 0:
            self.current_page -= 1
            return True
        
        return False


class Light(GameObject):
    """
    Light source class - objects that provide illumination
    """
    
    def __init__(self, **kwargs):
        flags = kwargs.get('flags', ObjectFlag.NONE)
        kwargs['flags'] = flags | ObjectFlag.LIGHT
        super().__init__(**kwargs)
        
        # Light-specific properties
        self.fuel_remaining: Optional[int] = kwargs.get('fuel_remaining')  # None = infinite
        self.fuel_type: str = kwargs.get('fuel_type', "battery")
        self.burn_rate: int = kwargs.get('burn_rate', 1)  # Fuel units per turn
    
    def turn_on(self) -> bool:
        """Turn on the light"""
        if self.fuel_remaining is not None and self.fuel_remaining <= 0:
            return False
        
        self.set_flag(ObjectFlag.ON)
        return True
    
    def turn_off(self) -> bool:
        """Turn off the light"""
        self.clear_flag(ObjectFlag.ON)
        return True
    
    def consume_fuel(self, amount: int = None) -> bool:
        """Consume fuel when light is on"""
        if not self.has_flag(ObjectFlag.ON):
            return True
        
        if self.fuel_remaining is None:
            return True  # Infinite fuel
        
        amount = amount or self.burn_rate
        self.fuel_remaining -= amount
        
        if self.fuel_remaining <= 0:
            self.fuel_remaining = 0
            self.turn_off()
            return False
        
        return True
    
    def refuel(self, amount: int):
        """Add fuel to the light source"""
        if self.fuel_remaining is not None:
            self.fuel_remaining += amount


class Furniture(GameObject):
    """
    Furniture class - large objects that can't be taken but may be containers/surfaces
    """
    
    def __init__(self, **kwargs):
        # Furniture is typically not takeable
        flags = kwargs.get('flags', ObjectFlag.NONE)
        flags &= ~ObjectFlag.TAKEABLE  # Remove takeable flag if present
        kwargs['flags'] = flags
        super().__init__(**kwargs)
        
        # Furniture-specific properties
        self.can_sit: bool = kwargs.get('can_sit', False)
        self.can_stand_on: bool = kwargs.get('can_stand_on', False)
        self.can_hide_behind: bool = kwargs.get('can_hide_behind', False)
        self.moveable: bool = kwargs.get('moveable', False)
    
    def move_furniture(self) -> bool:
        """Attempt to move the furniture"""
        if not self.moveable:
            return False
        
        # Mark as moved
        self.set_property('moved', True)
        
        # Might reveal something hidden
        hidden_items = self.get_property('reveals_when_moved', [])
        return len(hidden_items) > 0
    
    def search_under(self) -> List['GameObject']:
        """Search under the furniture"""
        return self.get_property('hidden_under', [])
    
    def search_behind(self) -> List['GameObject']:
        """Search behind the furniture"""
        if self.can_hide_behind:
            return self.get_property('hidden_behind', [])
        return []


# Utility functions for object management

#def create_object_from_data(data: Dict[str, Any], object_id: str) -> GameObject:
def create_game_object_from_data(object_id: str, data: Dict[str, Any]) -> GameObject:
    """
    Factory function to create game objects from JSON data.
    
    Determines object type based on:
    1. Explicit 'type' field
    2. Presence of type-specific fields (exits, schedule, etc.)
    3. Flags that indicate type
    
    Args:
        object_id: Unique identifier for the object
        data: Dictionary containing object data from JSON
        
    Returns:
        GameObject subclass instance
    """
    
    # Helper function to parse flags
    def parse_flags(flag_list: List[str]) -> ObjectFlag:
        """Parse string flags to ObjectFlag enum"""
        flags = ObjectFlag.NONE
        for flag_str in flag_list:
            try:
                # Handle both lowercase and uppercase
                flag_name = flag_str.upper()
                if hasattr(ObjectFlag, flag_name):
                    flags |= getattr(ObjectFlag, flag_name)
                else:
                    logger.warning(f"Unknown flag '{flag_str}' for object '{object_id}'")
            except Exception as e:
                logger.error(f"Error parsing flag '{flag_str}': {e}")
        return flags
    
    # Helper function to extract base properties
    def get_base_kwargs(data: Dict[str, Any], flags: ObjectFlag) -> Dict[str, Any]:
        """Extract common properties for all game objects"""
        return {
            'id': object_id,
            'name': data.get('name', object_id.replace('_', ' ').title()),
            'description': data.get('description', ''),
            'initial_description': data.get('initial_description'),
            'flags': flags,
            'synonyms': data.get('synonyms', []),
            'adjectives': data.get('adjectives', [])
        }
    
    # Parse flags first as they may influence type detection
    flags_list = data.get('flags', [])
    flags = parse_flags(flags_list)
    
    # Get explicit type or try to infer it
    obj_type = data.get('type', '').lower()
    
    # Type detection based on data structure and flags
    
    # 1. Check for Room (has exits or explicitly typed)
    if obj_type == 'room' or 'exits' in data:
        kwargs = get_base_kwargs(data, flags)
        kwargs.update({
            'exits': data.get('exits', {}),
            'light_needed': data.get('light_needed', False),
            'visited_description': data.get('visited_description', '')
        })
        obj = Room(**kwargs)
        logger.debug(f"Created Room: {object_id}")
        return obj
    
    # 2. Check for Character/NPC (has schedule, dialogue, or person flag)
    elif (obj_type in ['character', 'npc', 'person'] or 
          'schedule' in data or 
          'dialogue' in data or 
          'topics' in data or
          flags & ObjectFlag.PERSON):
        kwargs = get_base_kwargs(data, flags | ObjectFlag.PERSON)
        kwargs.update({
            'dialogue_state': data.get('dialogue_state', {}),
            'knowledge': data.get('knowledge', {}),
            'schedule': data.get('schedule', []),
            'topics': data.get('topics', {}),
            'current_activity': data.get('current_activity', 'idle'),
            'trust_level': data.get('trust_level', 0),
            'suspicion_level': data.get('suspicion_level', 0)
        })
        obj = Character(**kwargs)
        logger.debug(f"Created Character: {object_id}")
        return obj
    
    # 3. Check for Door (connects rooms)
    elif obj_type == 'door' or 'connects' in data:
        kwargs = get_base_kwargs(data, flags)
        connects = data.get('connects', [])
        if len(connects) != 2:
            logger.warning(f"Door {object_id} should connect exactly 2 rooms, got {len(connects)}")
            connects = (connects + [None, None])[:2]  # Ensure we have 2 elements
        
        kwargs.update({
            'connects': tuple(connects),
            'key_id': data.get('key_id'),
            'both_sides': data.get('both_sides', True),
            'locked_message': data.get('locked_message', "It's locked."),
            'closed_message': data.get('closed_message', "It's closed.")
        })
        obj = Door(**kwargs)
        logger.debug(f"Created Door: {object_id}")
        return obj
    
    # 4. Check for Container (has capacity or container flag)
    elif (obj_type == 'container' or 
          'capacity' in data or 
          flags & ObjectFlag.CONTAINER):
        kwargs = get_base_kwargs(data, flags | ObjectFlag.CONTAINER)
        kwargs.update({
            'capacity': data.get('capacity', 10),
            'key_id': data.get('key_id'),
            'open_message': data.get('open_message', "You open it."),
            'close_message': data.get('close_message', "You close it."),
            'already_open_message': data.get('already_open_message', "It's already open."),
            'already_closed_message': data.get('already_closed_message', "It's already closed.")
        })
        
        # Set initial open/locked state
        if data.get('is_open', False):
            kwargs['flags'] |= ObjectFlag.OPEN
        if data.get('is_locked', False):
            kwargs['flags'] |= ObjectFlag.LOCKED
            
        obj = Container(**kwargs)
        logger.debug(f"Created Container: {object_id}")
        return obj
    
    # 5. Check for Evidence (special item type for Deadline)
    elif obj_type == 'evidence' or data.get('evidence', False) or flags & ObjectFlag.EVIDENCE:
        kwargs = get_base_kwargs(data, flags | ObjectFlag.EVIDENCE | ObjectFlag.TAKEABLE)
        kwargs.update({
            'size': data.get('size', 1),
            'weight': data.get('weight', 1),
            'value': data.get('value', 0),
            'evidence_value': data.get('evidence_value', 10),
            'evidence_description': data.get('evidence_description', ''),
            'analysis_result': data.get('analysis_result', '')
        })
        
        # Evidence items might be readable
        if data.get('readable') or data.get('text'):
            kwargs['flags'] |= ObjectFlag.READABLE
            kwargs['text'] = data.get('text', '')
            
        obj = Evidence(**kwargs)
        logger.debug(f"Created Evidence: {object_id}")
        return obj
    
    # 6. Check for Player (special character type)
    elif obj_type == 'player':
        kwargs = get_base_kwargs(data, flags)
        kwargs.update({
            'max_carry': data.get('max_carry', 10),
            'score': data.get('score', 0)
        })
        obj = Player(**kwargs)
        logger.debug(f"Created Player: {object_id}")
        return obj
    
    # 7. Default to Item (basic takeable object)
    else:
        # Determine if it should be takeable
        if flags & ObjectFlag.TAKEABLE or data.get('takeable', False):
            flags |= ObjectFlag.TAKEABLE
            
        kwargs = get_base_kwargs(data, flags)
        kwargs.update({
            'size': data.get('size', 1),
            'weight': data.get('weight', 1),
            'value': data.get('value', 0)
        })
        
        # Check for readable items
        if data.get('readable') or data.get('text'):
            kwargs['flags'] |= ObjectFlag.READABLE
            kwargs['text'] = data.get('text', '')
        
        # Check for wearable items
        if data.get('wearable'):
            kwargs['flags'] |= ObjectFlag.WEARABLE
            kwargs['wear_message'] = data.get('wear_message', f"You put on the {kwargs['name']}.")
            kwargs['remove_message'] = data.get('remove_message', f"You take off the {kwargs['name']}.")
        
        # Check for edible/drinkable items
        if data.get('edible'):
            kwargs['flags'] |= ObjectFlag.EDIBLE
            kwargs['eat_message'] = data.get('eat_message', f"You eat the {kwargs['name']}.")
        
        if data.get('drinkable'):
            kwargs['flags'] |= ObjectFlag.DRINKABLE
            kwargs['drink_message'] = data.get('drink_message', f"You drink the {kwargs['name']}.")
        
        # Check for light sources
        if data.get('light_source'):
            kwargs['flags'] |= ObjectFlag.LIGHT
            kwargs['on_message'] = data.get('on_message', "You turn it on.")
            kwargs['off_message'] = data.get('off_message', "You turn it off.")
            if data.get('is_on', False):
                kwargs['flags'] |= ObjectFlag.ON
        
        obj = Item(**kwargs)
        logger.debug(f"Created Item: {object_id}")
    
    # Set additional custom properties that aren't part of constructor
    for key, value in data.items():
        # Skip properties we've already handled
        if key not in ['type', 'name', 'description', 'flags', 'synonyms', 
                      'adjectives', 'exits', 'capacity', 'key_id', 'connects',
                      'schedule', 'dialogue', 'topics', 'knowledge', 'size',
                      'weight', 'value', 'evidence_value', 'text', 'readable',
                      'wearable', 'edible', 'drinkable', 'light_source',
                      'is_open', 'is_locked', 'is_on', 'takeable',
                      'initial_description', 'visited_description',
                      'dialogue_state', 'current_activity', 'trust_level',
                      'suspicion_level', 'evidence_description', 'analysis_result',
                      'max_carry', 'score', 'light_needed', 'both_sides',
                      'location', 'contents']:  # These are handled elsewhere
            # Store as custom property
            obj.set_property(key, value)
            logger.debug(f"Set custom property '{key}' = '{value}' for {object_id}")
    
    # Handle initial location (will be set by WorldManager)
    if 'location' in data:
        obj.initial_location = data['location']
    
    # Handle initial contents (will be populated by WorldManager)
    if 'contents' in data:
        obj.initial_contents = data['contents']
    
    return obj

#######
#######  These might not be necessary... unclear
#######

# Additional classes that should be defined if not already present:

class Evidence(Item):
    """
    Special item class for evidence in Deadline
    Inherits from Item but adds evidence-specific properties
    """
    
    def __init__(self, evidence_value: int = 10, 
                 evidence_description: str = "",
                 analysis_result: str = "",
                 **kwargs):
        # Ensure evidence flag is set
        kwargs['flags'] = kwargs.get('flags', ObjectFlag.NONE) | ObjectFlag.EVIDENCE
        super().__init__(**kwargs)
        
        self.evidence_value = evidence_value
        self.evidence_description = evidence_description
        self.analysis_result = analysis_result
        self.analyzed = False
    
    def analyze(self) -> str:
        """Analyze the evidence"""
        self.analyzed = True
        if self.analysis_result:
            return self.analysis_result
        return f"You carefully examine the {self.name} but find nothing unusual."
    
    def get_description(self, detailed: bool = False) -> str:
        """Override to include evidence description when analyzed"""
        base_desc = super().get_description(detailed)
        if self.analyzed and self.evidence_description:
            return f"{base_desc}\n{self.evidence_description}"
        return base_desc


class Door(GameObject):
    """
    Door class - connects two rooms
    Can be locked, opened, closed
    """
    
    def __init__(self, connects: tuple, key_id: Optional[str] = None,
                 both_sides: bool = True, locked_message: str = "It's locked.",
                 closed_message: str = "It's closed.", **kwargs):
        super().__init__(**kwargs)
        
        self.connects = connects  # Tuple of (room1_id, room2_id)
        self.key_id = key_id  # ID of key that unlocks this door
        self.both_sides = both_sides  # Can be opened from both sides?
        self.locked_message = locked_message
        self.closed_message = closed_message
    
    def get_other_side(self, current_room_id: str) -> Optional[str]:
        """Get the room on the other side of this door"""
        if current_room_id == self.connects[0]:
            return self.connects[1]
        elif current_room_id == self.connects[1]:
            return self.connects[0]
        return None
    
    def can_pass_through(self, from_room_id: str) -> tuple[bool, str]:
        """Check if door can be passed through from given room"""
        if self.has_flag(ObjectFlag.LOCKED):
            return False, self.locked_message
        if not self.has_flag(ObjectFlag.OPEN):
            return False, self.closed_message
        if not self.both_sides and from_room_id != self.connects[0]:
            return False, "You can't go through from this side."
        return True, ""
    
    def unlock_with(self, key: GameObject) -> bool:
        """Attempt to unlock door with a key"""
        if not self.has_flag(ObjectFlag.LOCKED):
            return False  # Already unlocked
        if key.id == self.key_id:
            self.clear_flag(ObjectFlag.LOCKED)
            return True
        return False