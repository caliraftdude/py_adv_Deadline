# 4. 🔁 Mapping Constructs - ZIL to Python 3.13 Translation

## Core Language Construct Mappings

### 1. Function/Routine Definitions

#### ZIL Syntax
```zil
<ROUTINE FUNCTION-NAME (ARG1 ARG2 "OPTIONAL" (ARG3 DEFAULT-VALUE))
    #DECL ((ARG1) OBJECT (ARG2) STRING (ARG3) FIX)
    <TELL "Hello " .ARG2 CR>
    <RETURN .ARG1>>
```

#### Python 3.13 Equivalent
```python
def function_name(arg1: Object, arg2: str, arg3: int = DEFAULT_VALUE) -> Object:
    """ZIL routine translated to Python function"""
    print(f"Hello {arg2}")
    return arg1
```

#### Translation Notes
- ZIL angle brackets → Python function definition
- Optional arguments mapped to default parameters
- Type declarations become type hints
- TELL statements become print() calls
- DOT notation (.ARG) becomes direct variable access

### 2. Object System Translation

#### ZIL Object Definition
```zil
<OBJECT BRASS-KEY
    (IN PLAYER)
    (DESC "brass key")
    (LDESC "A small brass key with intricate engravings.")
    (SYNONYM KEY BRASS)
    (ADJECTIVE BRASS SMALL)
    (FLAGS TAKEBIT LIGHTBIT)
    (SIZE 2)
    (ACTION BRASS-KEY-ACTION)>
```

#### Python 3.13 Class System
```python
class BrassKey(GameObject):
    def __init__(self):
        super().__init__(
            name="brass key",
            short_desc="brass key", 
            long_desc="A small brass key with intricate engravings.",
            synonyms=["key", "brass"],
            adjectives=["brass", "small"],
            flags={Flag.TAKEABLE, Flag.LIGHT_SOURCE},
            size=2,
            location=None  # Will be set to player inventory
        )
    
    def action(self, verb: Verb, dobj: GameObject = None) -> ActionResult:
        """Handle actions performed on this object"""
        return brass_key_action(verb, self, dobj)

# Object registry for runtime lookup
game_objects.register("brass-key", BrassKey)
```

#### Object Hierarchy Mapping
```python
# ZIL containment system
# <OBJECT ITEM (IN CONTAINER)>

class GameObject:
    def __init__(self, location: 'GameObject' = None):
        self.location = location
        self.contents: List['GameObject'] = []
        
    def move_to(self, new_location: 'GameObject'):
        """Move object to new container (ZIL MOVE function)"""
        if self.location:
            self.location.contents.remove(self)
        self.location = new_location
        if new_location:
            new_location.contents.append(self)
```

### 3. Property System

#### ZIL Property Access
```zil
<GETP OBJECT PROPERTY>          ; Get property value
<PUTP OBJECT PROPERTY VALUE>    ; Set property value
<GETPT OBJECT PROPERTY>         ; Get property table entry
```

#### Python Property System
```python
class GameObject:
    def __init__(self):
        self._properties: Dict[str, Any] = {}
    
    def get_property(self, prop_name: str, default=None):
        """ZIL GETP equivalent"""
        return self._properties.get(prop_name, default)
    
    def set_property(self, prop_name: str, value: Any):
        """ZIL PUTP equivalent"""
        self._properties[prop_name] = value
    
    def has_property(self, prop_name: str) -> bool:
        """Check if property exists"""
        return prop_name in self._properties

# Pythonic property access using descriptors
class GameProperty:
    def __init__(self, prop_name: str, default=None):
        self.prop_name = prop_name
        self.default = default
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.get_property(self.prop_name, self.default)
    
    def __set__(self, obj, value):
        obj.set_property(self.prop_name, value)

class Room(GameObject):
    description = GameProperty("description", "")
    north_exit = GameProperty("north", None)
    visited = GameProperty("visited", False)
```

### 4. Conditional Logic Translation

#### ZIL COND Statement
```zil
<COND (<EQUAL? .ARG "yes"> <TELL "Affirmative" CR> <RTRUE>)
      (<EQUAL? .ARG "no"> <TELL "Negative" CR> <RFALSE>) 
      (T <TELL "Unknown response" CR> <RFALSE>)>
```

#### Python Conditional Logic
```python
def handle_response(arg: str) -> bool:
    """ZIL COND translated to Python if-elif-else"""
    if arg == "yes":
        print("Affirmative")
        return True
    elif arg == "no":
        print("Negative")
        return False
    else:
        print("Unknown response")
        return False

# Alternative using match statement (Python 3.10+)
def handle_response_modern(arg: str) -> bool:
    match arg:
        case "yes":
            print("Affirmative")
            return True
        case "no":
            print("Negative")
            return False
        case _:
            print("Unknown response")
            return False
```

### 5. Parser System Translation

#### ZIL Syntax Rules
```zil
<SYNTAX TAKE OBJECT = V-TAKE>
<SYNTAX GET OBJECT = V-TAKE>
<SYNTAX PICK UP OBJECT = V-TAKE>
<SYNTAX PUT OBJECT1 IN OBJECT2 = V-PUT PRE-PUT>
```

#### Python Parser Framework
```python
class SyntaxRule:
    def __init__(self, pattern: str, verb_handler: callable, prehandler: callable = None):
        self.pattern = pattern
        self.verb_handler = verb_handler
        self.prehandler = prehandler
        self.regex = self._compile_pattern(pattern)
    
    def _compile_pattern(self, pattern: str) -> re.Pattern:
        """Convert ZIL syntax pattern to regex"""
        # TAKE OBJECT -> r"take (\w+)"
        # PUT OBJECT1 IN OBJECT2 -> r"put (\w+) in (\w+)"
        return re.compile(pattern.lower())

class Parser:
    def __init__(self):
        self.syntax_rules = [
            SyntaxRule("take OBJECT", verb_take),
            SyntaxRule("get OBJECT", verb_take), 
            SyntaxRule("pick up OBJECT", verb_take),
            SyntaxRule("put OBJECT in OBJECT", verb_put, pre_put),
        ]
        self.vocabulary = Vocabulary()
    
    def parse(self, command: str) -> ParseResult:
        """Main parsing logic - ZIL parser equivalent"""
        command = command.strip().lower()
        
        # Try to match syntax patterns
        for rule in self.syntax_rules:
            match = rule.regex.match(command)
            if match:
                return self._process_match(rule, match)
        
        return ParseResult.error("I don't understand that.")
```

### 6. Global Variables and Constants

#### ZIL Global Definitions
```zil
<GLOBAL SCORE 0>
<GLOBAL MOVES 0>
<GLOBAL WINNER <>>
<CONSTANT MAX-SCORE 100>
<CONSTANT TIME-LIMIT 720>  ; 12 hours in minutes
```

#### Python Global State Management
```python
class GameState:
    """Centralized game state management"""
    def __init__(self):
        self.score: int = 0
        self.moves: int = 0
        self.winner: Optional[str] = None
        self.current_time: int = 480  # 8:00 AM start
        
    # Singleton pattern for global access
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'GameState':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Constants
class GameConstants:
    MAX_SCORE = 100
    TIME_LIMIT = 720  # 12 hours in minutes
    START_TIME = 480  # 8:00 AM

# Global access functions (ZIL-style)
def get_score() -> int:
    return GameState.get_instance().score

def set_score(value: int):
    GameState.get_instance().score = value
```

### 7. Control Flow Constructs

#### ZIL Control Structures
```zil
; Loops
<REPEAT ()
    <COND (<NOT <NEXT? ,ROOM-LIST>> <RETURN>)>
    <SET CURRENT-ROOM <NEXT ,ROOM-LIST>>
    <DO-SOMETHING .CURRENT-ROOM>>

; Conditional returns
<COND (<EQUAL? .INPUT "quit"> <QUIT>)>
```

#### Python Control Flow
```python
# Loop translation
def process_all_rooms():
    """ZIL REPEAT loop equivalent"""
    for room in room_list:
        do_something(room)

# Early returns
def handle_input(input_text: str):
    """ZIL conditional quit equivalent"""
    if input_text == "quit":
        quit_game()
        return
    # Continue processing...
```

### 8. String Handling and Output

#### ZIL Text Output
```zil
<TELL "You see a " D .OBJECT " here." CR>
<TELL "Score: " N .SCORE " out of " N ,MAX-SCORE CR>
<TELL C 65>  ; Print character 'A'
<TELL CR>    ; Print newline
```

#### Python String Formatting
```python
def tell_object_description(obj: GameObject):
    """ZIL TELL with object description"""
    print(f"You see a {obj.short_desc} here.")

def tell_score(score: int):
    """ZIL TELL with numbers"""
    print(f"Score: {score} out of {GameConstants.MAX_SCORE}")

def tell_char(char_code: int):
    """ZIL character output"""
    print(chr(char_code), end='')

def tell_newline():
    """ZIL CR (carriage return)"""
    print()

# Modern Python f-string approach
class OutputManager:
    @staticmethod
    def format_message(template: str, **kwargs) -> str:
        """Enhanced text formatting"""
        return template.format(**kwargs)
    
    @staticmethod
    def tell(message: str, newline: bool = True):
        """Enhanced TELL function with optional newline"""
        print(message, end='\n' if newline else '')
```

### 9. Memory Management and Garbage Collection

#### ZIL Memory Model
```zil
; ZIL automatic memory management
; Objects created and destroyed automatically
; Stack-based local variables
; Property tables managed by runtime
```

#### Python Memory Management
```python
# Python automatic garbage collection
# Reference counting + cycle detection
# Context managers for resource cleanup

class GameObjectManager:
    """Manage game object lifecycle"""
    def __init__(self):
        self._objects: Dict[str, GameObject] = {}
        self._active_objects: Set[GameObject] = set()
    
    def create_object(self, obj_id: str, obj_class: type) -> GameObject:
        """Create and register object"""
        obj = obj_class()
        obj.id = obj_id
        self._objects[obj_id] = obj
        self._active_objects.add(obj)
        return obj
    
    def destroy_object(self, obj_id: str):
        """Clean up object references"""
        if obj_id in self._objects:
            obj = self._objects[obj_id]
            self._active_objects.discard(obj)
            # Remove from containers
            if obj.location:
                obj.location.contents.remove(obj)
            # Clear references
            del self._objects[obj_id]
```

### 10. Event System and Time Management

#### ZIL Daemon/Fuse System
```zil
<ROUTINE CLOCK-DAEMON ()
    <SET GAME-TIME <+ ,GAME-TIME 1>>
    <COND (<G? ,GAME-TIME ,TIME-LIMIT>
           <TELL "Time runs out!" CR>
           <FINISH>)>>

; Start daemon
<ENABLE <DAEMON CLOCK-DAEMON>>
```

#### Python Event System
```python
import heapq
from typing import Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class GameEvent:
    time: int
    callback: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: int = 0
    
    def __lt__(self, other):
        return (self.time, self.priority) < (other.time, other.priority)

class TimeManager:
    """ZIL daemon/fuse system equivalent"""
    def __init__(self):
        self.current_time = 0
        self.events: List[GameEvent] = []
        self.daemons: Dict[str, Callable] = {}
        
    def schedule_event(self, delay: int, callback: Callable, *args, **kwargs):
        """ZIL FUSE equivalent - one-time event"""
        event = GameEvent(
            time=self.current_time + delay,
            callback=callback,
            args=args,
            kwargs=kwargs or {}
        )
        heapq.heappush(self.events, event)
    
    def register_daemon(self, name: str, callback: Callable):
        """ZIL DAEMON equivalent - recurring event"""
        self.daemons[name] = callback
    
    def advance_time(self, minutes: int = 1):
        """Advance game time and process events"""
        self.current_time += minutes
        
        # Process scheduled events
        while self.events and self.events[0].time <= self.current_time:
            event = heapq.heappop(self.events)
            event.callback(*event.args, **event.kwargs)
        
        # Run daemons every time tick
        for daemon_name, daemon_func in self.daemons.items():
            try:
                daemon_func()
            except Exception as e:
                print(f"Daemon {daemon_name} error: {e}")

# Clock daemon implementation
def clock_daemon():
    """Main game clock - ZIL CLOCK-DAEMON equivalent"""
    game_state = GameState.get_instance()
    
    if game_state.current_time >= GameConstants.TIME_LIMIT:
        print("Time runs out!")
        end_game("time_limit")
```

### 11. Save/Load System Translation

#### ZIL Save System (conceptual)
```zil
; ZIL save/restore handled by Z-machine
; SAVE and RESTORE opcodes
; Automatic state serialization
```

#### Python Persistence System
```python
import pickle
import json
from pathlib import Path
from typing import Dict, Any

class SaveGameManager:
    """Handle game state persistence"""
    
    @staticmethod
    def save_game(filename: str, game_state: GameState) -> bool:
        """Save complete game state - ZIL SAVE equivalent"""
        try:
            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'game_state': game_state.serialize(),
                'objects': {obj.id: obj.serialize() 
                           for obj in GameObjectManager.get_all_objects()},
                'world_state': WorldState.serialize(),
                'time_events': TimeManager.get_instance().serialize()
            }
            
            with open(filename, 'wb') as f:
                pickle.dump(save_data, f)
            
            return True
            
        except Exception as e:
            print(f"Save failed: {e}")
            return False
    
    @staticmethod
    def load_game(filename: str) -> bool:
        """Load game state - ZIL RESTORE equivalent"""
        try:
            if not Path(filename).exists():
                return False
                
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            
            # Validate save file version
            if save_data.get('version') != '1.0':
                print("Incompatible save file version")
                return False
            
            # Restore game state
            GameState.get_instance().deserialize(save_data['game_state'])
            GameObjectManager.restore_objects(save_data['objects'])
            WorldState.deserialize(save_data['world_state'])
            TimeManager.get_instance().deserialize(save_data['time_events'])
            
            return True
            
        except Exception as e:
            print(f"Load failed: {e}")
            return False
```

## Design Pattern Adaptations

### 1. Command Pattern Implementation

#### ZIL Verb System
```zil
<ROUTINE V-TAKE ()
    <COND (<NOT <HELD? ,PRSO>>
           <MOVE ,PRSO ,PLAYER>
           <TELL "Taken." CR>)
          (T <TELL "You already have that." CR>)>>
```

#### Python Command Pattern
```python
from abc import ABC, abstractmethod

class Command(ABC):
    """Base command interface"""
    @abstractmethod
    def execute(self) -> ActionResult:
        pass
    
    @abstractmethod
    def can_execute(self) -> bool:
        pass

class TakeCommand(Command):
    """ZIL V-TAKE equivalent"""
    def __init__(self, obj: GameObject, player: Player):
        self.obj = obj
        self.player = player
    
    def can_execute(self) -> bool:
        return (self.obj.has_flag(Flag.TAKEABLE) and 
                self.obj.location != self.player and
                self.player.can_carry(self.obj))
    
    def execute(self) -> ActionResult:
        if not self.can_execute():
            return ActionResult.failure("You can't take that.")
        
        self.obj.move_to(self.player)
        return ActionResult.success("Taken.")

class VerbProcessor:
    """Central verb processing system"""
    def __init__(self):
        self.verbs = {
            'take': TakeCommand,
            'get': TakeCommand,
            'pick': TakeCommand,
        }
    
    def process_verb(self, verb: str, dobj: GameObject) -> ActionResult:
        """Process verb command - ZIL parser equivalent"""
        command_class = self.verbs.get(verb)
        if not command_class:
            return ActionResult.failure("I don't understand that verb.")
        
        command = command_class(dobj, GameState.get_instance().player)
        return command.execute()
```

### 2. Observer Pattern for Events

#### ZIL Event Handling (implicit)
```zil
; Events handled through property changes
; No explicit observer pattern
```

#### Python Observer Pattern
```python
from typing import Protocol, Set

class GameEventListener(Protocol):
    def on_event(self, event_type: str, data: Dict[str, Any]):
        """Handle game events"""
        ...

class EventManager:
    """Centralized event system"""
    def __init__(self):
        self.listeners: Dict[str, Set[GameEventListener]] = {}
    
    def subscribe(self, event_type: str, listener: GameEventListener):
        """Register event listener"""
        if event_type not in self.listeners:
            self.listeners[event_type] = set()
        self.listeners[event_type].add(listener)
    
    def emit(self, event_type: str, data: Dict[str, Any] = None):
        """Notify all listeners of event"""
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener.on_event(event_type, data or {})

# Usage example
class Character(GameObject, GameEventListener):
    def on_event(self, event_type: str, data: Dict[str, Any]):
        """React to game events"""
        if event_type == "player_entered_room":
            room = data.get("room")
            if room == self.location:
                self.react_to_player()
```

### 3. State Machine Pattern for NPCs

#### ZIL Character States (implicit)
```zil
; Character behavior through property flags
; State changes via property updates
```

#### Python State Machine
```python
from enum import Enum, auto
from typing import Optional

class NPCState(Enum):
    IDLE = auto()
    TALKING = auto()
    MOVING = auto()
    SUSPICIOUS = auto()
    HOSTILE = auto()

class NPCStateMachine:
    """Manage NPC behavior states"""
    def __init__(self, initial_state: NPCState = NPCState.IDLE):
        self.current_state = initial_state
        self.transitions = {
            NPCState.IDLE: [NPCState.TALKING, NPCState.MOVING],
            NPCState.TALKING: [NPCState.IDLE, NPCState.SUSPICIOUS],
            NPCState.MOVING: [NPCState.IDLE],
            NPCState.SUSPICIOUS: [NPCState.HOSTILE, NPCState.IDLE],
            NPCState.HOSTILE: []  # Terminal state
        }
    
    def can_transition_to(self, new_state: NPCState) -> bool:
        """Check if state transition is valid"""
        return new_state in self.transitions.get(self.current_state, [])
    
    def transition_to(self, new_state: NPCState) -> bool:
        """Change to new state if valid"""
        if self.can_transition_to(new_state):
            old_state = self.current_state
            self.current_state = new_state
            self.on_state_changed(old_state, new_state)
            return True
        return False
    
    def on_state_changed(self, old_state: NPCState, new_state: NPCState):
        """Handle state transition effects"""
        pass

class Character(GameObject):
    def __init__(self):
        super().__init__()
        self.state_machine = NPCStateMachine()
        self.dialogue_state = {}
        self.schedule = []
    
    def update(self):
        """Called every game turn - ZIL daemon equivalent"""
        current_state = self.state_machine.current_state
        
        if current_state == NPCState.MOVING:
            self.execute_movement()
        elif current_state == NPCState.TALKING:
            self.update_conversation()
```

## Performance Considerations

### Memory Efficiency
```python
# Use __slots__ for game objects to reduce memory overhead
class GameObject:
    __slots__ = ['id', 'location', 'contents', '_properties', 'flags']
    
    def __init__(self):
        self.id: str = ""
        self.location: Optional['GameObject'] = None
        self.contents: List['GameObject'] = []
        self._properties: Dict[str, Any] = {}
        self.flags: Set[Flag] = set()
```

### String Interning for Vocabulary
```python
import sys

class Vocabulary:
    """Efficient word storage using string interning"""
    def __init__(self):
        self.words = {}
        self.synonyms = {}
    
    def add_word(self, word: str, obj_id: str):
        """Add word with automatic interning"""
        interned_word = sys.intern(word.lower())
        self.words[interned_word] = obj_id
```

### Lazy Loading for Large Game Worlds
```python
class RoomManager:
    """Lazy load room descriptions and properties"""
    def __init__(self):
        self._room_cache = {}
        self._room_data_path = "data/rooms/"
    
    def get_room(self, room_id: str) -> Room:
        """Load room on demand"""
        if room_id not in self._room_cache:
            self._room_cache[room_id] = self._load_room(room_id)
        return self._room_cache[room_id]
```

This comprehensive mapping provides the foundation for translating ZIL's unique constructs into idiomatic Python 3.13 code while preserving the original game's functionality and structure. The patterns established here will guide the actual code translation process in subsequent steps.