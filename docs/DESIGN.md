# 7_code_translation/docs/DESIGN.md
# Design Document

## Original ZIL to Python Translation

This port translates the original ZIL (Zork Implementation Language) code to Python 3.13 while preserving all game logic and functionality.

## Key Translation Mappings

### ZIL Constructs → Python

- `<OBJECT>` → `GameObject` class
- `<ROOM>` → `Room` class
- `<ROUTINE>` → Python methods
- `<COND>` → if/elif/else
- `<TELL>` → print() with formatting
- `GETP/PUTP` → get_property/set_property
- `FSET/FCLEAR` → set_flag/clear_flag
- `IN?` → is_in() method
- `MOVE` → move_to() method

### Property System

ZIL's property system is implemented using Python dictionaries with getter/setter methods that match the original semantics.

### Flag System

ZIL's bit flags are implemented using Python's Flag enum, providing type-safe flag operations.

### Parser

The parser recreates ZIL's natural language processing using:
- Regex patterns for syntax matching
- Vocabulary lookup tables
- Disambiguation logic

### Time System

ZIL's daemon/fuse system is implemented using:
- Event scheduler with priority queue
- Recurring daemons
- One-time scheduled events

## Data-Driven Design

All game-specific content is stored in JSON files, making it easy to:
- Modify game content without changing code
- Create new games using the same engine
- Validate game data structure

## Preservation of Original Gameplay

The port faithfully recreates:
- All rooms and locations
- All objects and their properties
- All NPC behaviors and schedules
- The complete murder mystery plot
- Multiple solution paths
- Time-based events
- Evidence collection system