# Deadline Python Port - Design Document

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Systems](#core-systems)
4. [Translation Mappings](#translation-mappings)
5. [Data Format](#data-format)
6. [Implementation Details](#implementation-details)
7. [Performance Considerations](#performance-considerations)
8. [Future Improvements](#future-improvements)

## Overview

This document describes the technical design of the Deadline Python port, translated from the original ZIL (Zork Implementation Language) source code to Python 3.13. The port maintains complete fidelity to the original game while modernizing the implementation.

### Design Goals
1. **Preserve Original Gameplay**: All puzzles, mechanics, and story elements intact
2. **Modern Architecture**: Clean, maintainable Python code
3. **Data-Driven Design**: Separate engine from content
4. **Extensibility**: Support for creating new games
5. **Performance**: Responsive gameplay experience

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                       │
│                    (Console/Terminal)                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                    Game Engine Core                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Parser  │  │ Commands │  │   Time   │  │  I/O   │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                    World Manager                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Rooms   │  │ Objects  │  │NPCs/Chars│  │Evidence│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  Data Layer (JSON)                       │
│         game_data.json, vocabulary.json, etc.           │
└─────────────────────────────────────────────────────────┘
```

### Module Organization

```python
deadline/
├── core/               # Core engine components
│   ├── game_engine.py      # Main game loop and state
│   ├── game_object.py      # Object hierarchy
│   ├── flags.py            # Object flags/properties
│   └── exceptions.py       # Custom exceptions
│
├── parser/             # Natural language processing
│   ├── parser.py           # Main parser
│   ├── vocabulary.py       # Word definitions
│   ├── syntax.py           # Grammar rules
│   └── disambiguator.py    # Ambiguity resolution
│
├── commands/           # Command implementations
│   ├── base_command.py     # Command base class
│   ├── movement.py         # Movement commands
│   ├── manipulation.py     # Object manipulation
│   ├── examination.py      # Look/examine commands
│   ├── communication.py    # NPC interaction
│   └── meta_commands.py    # Save/load/quit etc.
│
├── world/              # World state management
│   ├── world_manager.py    # Central world state
│   ├── room_manager.py     # Room navigation
│   ├── character_manager.py # NPC management
│   └── evidence_manager.py  # Evidence tracking
│
├── time/               # Time and scheduling
│   ├── time_manager.py     # Game clock
│   ├── scheduler.py        # Event scheduling
│   └── events.py           # Event definitions
│
├── io/                 # Input/Output
│   ├── interface.py        # User interface
│   ├── save_system.py      # Save/load games
│   └── output_formatter.py # Text formatting
│
└── data/               # Game content (JSON)
    ├── game_data.json      # All game content
    ├── vocabulary.json     # Parser vocabulary
    ├── syntax_rules.json   # Command patterns
    └── schedules.json      # Timed events
```

## Core Systems

### Object System

The object hierarchy mirrors ZIL's object-oriented approach:

```python
GameObject (base class)
├── Room          # Locations with exits
├── Item          # Takeable objects
├── Container     # Objects that hold other objects
├── Character     # NPCs with dialogue and schedules
│   └── Player    # Player character
├── Door          # Connections between rooms
└── Evidence      # Special items for case solving
```

#### Key Object Properties
- **ID**: Unique identifier
- **Name**: Display name
- **Description**: Detailed text
- **Flags**: Behavioral properties (takeable, locked, etc.)
- **Location**: Current container/room
- **Contents**: Objects contained within

### Flag System

Flags control object behavior, translated from ZIL's bit flags:

```python
class ObjectFlag(Flag):
    TAKEABLE = auto()      # Can be picked up (TAKEBIT)
    CONTAINER = auto()     # Can contain objects (CONTBIT)
    OPEN = auto()          # Container is open (OPENBIT)
    LOCKED = auto()        # Is locked (LOCKEDBIT)
    LIGHT = auto()         # Provides light (LIGHTBIT)
    READABLE = auto()      # Can be read (READBIT)
    EVIDENCE = auto()      # Is evidence (custom)
    SEARCHED = auto()      # Has been searched
    # ... more flags
```

### Parser System

The parser uses a multi-stage approach:

1. **Tokenization**: Split input into words
2. **Vocabulary Lookup**: Match words to game vocabulary
3. **Pattern Matching**: Match against syntax rules
4. **Disambiguation**: Resolve ambiguous references
5. **Command Creation**: Generate command object

```python
# Parser Pipeline
input_text = "take the brass key from the table"
    ↓ tokenize
tokens = ["take", "brass", "key", "from", "table"]
    ↓ vocabulary lookup
words = [VERB("take"), ADJ("brass"), NOUN("key"), PREP("from"), NOUN("table")]
    ↓ pattern match
pattern = "verb [adj] noun prep noun"
    ↓ disambiguate
objects = [brass_key, coffee_table]
    ↓ create command
command = TakeCommand(direct_obj=brass_key, indirect_obj=coffee_table)
```

### Time System

The time system manages the game clock and scheduled events:

```python
class TimeManager:
    def __init__(self, start_time: int):
        self.current_time = start_time  # Minutes since midnight
        self.scheduled_events = []      # Priority queue of events
        self.recurring_events = []      # Daemon-like events
    
    def advance_time(self, minutes: int):
        """Advance game time and trigger events"""
        new_time = self.current_time + minutes
        
        # Process scheduled events
        while self.scheduled_events:
            event = self.scheduled_events[0]
            if event.time <= new_time:
                event.execute()
                heappop(self.scheduled_events)
            else:
                break
        
        self.current_time = new_time
```

## Translation Mappings

### ZIL to Python Translations

| ZIL Construct | Python Implementation | Notes |
|---------------|----------------------|-------|
| `<OBJECT>` | `GameObject` class | Object-oriented approach |
| `<ROOM>` | `Room` class | Inherits from GameObject |
| `<ROUTINE>` | Python method/function | Direct translation |
| `<COND>` | `if/elif/else` | Standard conditionals |
| `<TELL>` | `print()` with formatting | Output system |
| `GETP/PUTP` | `get_property/set_property` | Property access |
| `FSET/FCLEAR` | `set_flag/clear_flag` | Flag manipulation |
| `IN?` | `is_in()` method | Containment check |
| `MOVE` | `move_to()` method | Object relocation |
| `PRINTI/PRINTR` | String formatting | Text output |
| `RANDOM` | `random.choice/randint` | Random generation |
| `GOTO` | Function calls | Structured programming |

### Property System Mapping

ZIL properties are implemented as Python attributes:

```python
# ZIL: <GETP OBJECT PROPERTY>
# Python:
value = obj.get_property('property_name')

# ZIL: <PUTP OBJECT PROPERTY VALUE>
# Python:
obj.set_property('property_name', value)
```

## Data Format

### JSON Structure

All game content is stored in structured JSON:

```json
{
  "metadata": {
    "title": "Deadline",
    "author": "Marc Blank",
    "version": "1.0.0"
  },
  
  "config": {
    "max_score": 100,
    "start_time": 480,
    "time_limit": 720
  },
  
  "rooms": {
    "room_id": {
      "name": "Room Name",
      "description": "Detailed description...",
      "exits": {
        "north": "other_room_id",
        "east": "another_room_id"
      },
      "contents": ["object_id1", "object_id2"],
      "flags": ["VISITED", "LIGHT_NEEDED"],
      "properties": {
        "custom_prop": "value"
      }
    }
  },
  
  "objects": {
    "object_id": {
      "type": "item|container|evidence",
      "name": "Object Name",
      "description": "Description...",
      "flags": ["TAKEABLE", "READABLE"],
      "location": "room_id",
      "properties": {
        "weight": 5,
        "value": 10
      }
    }
  },
  
  "characters": {
    "character_id": {
      "name": "Character Name",
      "description": "Description...",
      "location": "room_id",
      "dialogue": {
        "topic": "Response text..."
      },
      "schedule": [
        {
          "time": 540,
          "action": "move",
          "target": "room_id"
        }
      ]
    }
  }
}
```

## Implementation Details

### Command Processing Pipeline

```python
def process_command(self, input_text: str) -> CommandResult:
    """Main command processing pipeline"""
    
    # 1. Parse input
    parse_result = self.parser.parse(input_text)
    if not parse_result.is_valid:
        return CommandResult.error(parse_result.error_message)
    
    # 2. Get command handler
    command = self.command_processor.get_command(parse_result.verb)
    if not command:
        return CommandResult.error(f"Unknown command: {parse_result.verb}")
    
    # 3. Validate command
    if not command.can_execute(parse_result):
        return CommandResult.failure("You can't do that.")
    
    # 4. Execute command
    result = command.execute(parse_result)
    
    # 5. Update game state
    if result.consumed_time:
        self.time_manager.advance_time(1)
    
    if result.update_state:
        self.world_manager.update_state()
    
    return result
```

### Object Resolution

Objects are resolved through multiple scopes:

```python
def resolve_object(self, name: str, context: Context) -> GameObject:
    """Resolve object name to game object"""
    
    # 1. Check inventory
    obj = self.find_in_inventory(name)
    if obj:
        return obj
    
    # 2. Check current room
    obj = self.find_in_room(name, context.current_room)
    if obj:
        return obj
    
    # 3. Check containers in room
    for container in context.current_room.get_containers():
        if container.is_open:
            obj = self.find_in_container(name, container)
            if obj:
                return obj
    
    # 4. Check global objects
    return self.find_global_object(name)
```

### Save System

The save system serializes the complete game state:

```python
def save_game(self, filename: str) -> bool:
    """Save complete game state"""
    save_data = {
        'version': self.VERSION,
        'timestamp': datetime.now().isoformat(),
        'game_state': {
            'score': self.score,
            'moves': self.moves,
            'time': self.current_time,
            'flags': self.flags.value
        },
        'world_state': self.world_manager.serialize(),
        'evidence': self.evidence_manager.serialize(),
        'parser_state': self.parser.get_state()
    }
    
    # Compress and save
    with gzip.open(filename, 'wt') as f:
        json.dump(save_data, f)
    
    return True
```

## Performance Considerations

### Optimization Strategies

1. **Caching**: Frequently accessed data is cached
   ```python
   @lru_cache(maxsize=128)
   def find_object(self, obj_id: str) -> GameObject:
       # Object lookup with caching
   ```

2. **Lazy Loading**: Data loaded only when needed
   ```python
   @property
   def long_description(self):
       if not self._long_desc_loaded:
           self._long_desc = self.load_description()
           self._long_desc_loaded = True
       return self._long_desc
   ```

3. **Compiled Patterns**: Regex patterns pre-compiled
   ```python
   class Parser:
       def __init__(self):
           self.patterns = {
               'verb_noun': re.compile(r'^(\w+)\s+(.+)$'),
               # More patterns...
           }
   ```

4. **String Interning**: Common strings interned
   ```python
   COMMON_WORDS = {sys.intern(w) for w in [
       'the', 'a', 'an', 'and', 'or', 'but'
   ]}
   ```

### Memory Management

- Object pooling for frequently created/destroyed objects
- Weak references for circular dependencies
- Explicit cleanup in `__del__` methods where needed

## Future Improvements

### Planned Enhancements

1. **Enhanced Parser**
   - Support for compound commands
   - Better pronoun resolution
   - Typo correction

2. **Improved Evidence System**
   - Evidence chain tracking
   - Deduction hints
   - Case notebook

3. **Extended NPC AI**
   - Dynamic dialogue based on game state
   - Reactive behaviors
   - Emotional states

4. **Quality of Life Features**
   - Command history with arrow keys
   - Tab completion
   - Undo/redo system
   - Built-in hints

5. **Technical Improvements**
   - Async I/O for better responsiveness
   - Plugin system for extensions
   - Scripting support for custom content
   - Web-based interface option

### Extensibility Points

The architecture provides several extension points:

```python
# Custom command example
@command('investigate', 'search')
class InvestigateCommand(Command):
    def execute(self, parse_result):
        # Custom investigation logic
        pass

# Custom object type
class Weapon(Item):
    def __init__(self, damage: int, **kwargs):
        super().__init__(**kwargs)
        self.damage = damage
    
    def use_on(self, target: GameObject):
        # Weapon-specific behavior
        pass

# Event hook example
@event_handler('on_enter_room')
def check_for_clues(room: Room, player: Player):
    if room.has_flag(ObjectFlag.CRIME_SCENE):
        # Special crime scene logic
        pass
```

## Testing Strategy

### Test Categories

1. **Unit Tests**: Individual components
2. **Integration Tests**: System interactions
3. **Game Logic Tests**: Puzzle solutions
4. **Regression Tests**: Original game behavior
5. **Performance Tests**: Response times

### Test Coverage Goals

- Core Systems: >90% coverage
- Commands: 100% coverage
- Parser: >85% coverage
- Game Logic: 100% critical paths

## Conclusion

This port successfully translates Deadline from ZIL to Python while:
- Preserving all original gameplay
- Modernizing the architecture
- Enabling future enhancements
- Maintaining performance
- Supporting extensibility

The data-driven design allows for easy creation of new interactive fiction games using the same engine, while the modular architecture ensures maintainability and testability.