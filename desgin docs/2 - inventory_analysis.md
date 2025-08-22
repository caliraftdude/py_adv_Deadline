# 2. 📦 Inventory and Analysis - Deadline ZIL Codebase

## File and Module Structure

Based on the analysis of the Deadline repository and ZIL language patterns, the codebase follows Infocom's standard structure derived from Zork's original architecture.

### Core ZIL Files (Expected Structure)

#### Primary Game Files
- **`DEADLINE.ZIL`** - Main game initialization and global definitions
- **`PARSER.ZIL`** - Natural language parsing engine
- **`VERBS.ZIL`** - Verb implementations and command handlers  
- **`OBJECTS.ZIL`** - Game objects (rooms, items, characters) definitions
- **`GLOBALS.ZIL`** - Global variables and constants
- **`SYNTAX.ZIL`** - Grammar definitions and syntax rules
- **`CLOCK.ZIL`** - Time-based event scheduling system
- **`PEOPLE.ZIL`** - NPC behavior and character interactions

#### Supporting Files
- **`ROOMS.ZIL`** - Room descriptions and geography
- **`ITEMS.ZIL`** - Item properties and behaviors
- **`ACTIONS.ZIL`** - Action routines and implementations
- **`DEMONS.ZIL`** - Background processes and timed events
- **`VOCAB.ZIL`** - Vocabulary and word definitions
- **`DEBUG.ZIL`** - Debugging and testing utilities

### ZIL Language-Specific Constructs

#### Object System
```zil
<OBJECT ROOM-NAME
    (IN ROOMS)
    (DESC "Room description")
    (LDESC "Long description")
    (FLAGS LIGHTBIT LANDBIT)
    (NORTH TO NEXT-ROOM)
    (ACTION ROOM-ACTION-ROUTINE)>
```

#### Routine Definitions
```zil
<ROUTINE ROUTINE-NAME (ARG1 ARG2 "OPTIONAL" (ARG3 DEFAULT-VALUE))
    #DECL ((ARG1) OBJECT (ARG2) STRING (ARG3) FIX)
    ...routine body...>
```

#### Property Access
```zil
<GETP OBJECT PROPERTY>
<PUTP OBJECT PROPERTY VALUE>
```

#### Conditional Logic
```zil
<COND (<TEST1> <ACTION1>)
      (<TEST2> <ACTION2>)
      (T <DEFAULT-ACTION>)>
```

## Language-Specific Features Analysis

### ZIL Unique Characteristics

#### 1. Angle Bracket Syntax
- **Function Calls**: `<FUNCTION ARG1 ARG2>`
- **Object Creation**: `<OBJECT ...>`
- **Routine Definition**: `<ROUTINE ...>`
- **Conditional Logic**: `<COND ...>`

#### 2. Object-Oriented Features
- **Object Hierarchy**: Objects can contain other objects
- **Property System**: Objects have named properties with values
- **Inheritance**: Objects can inherit from parent objects
- **Method Dispatch**: Actions can be attached to objects

#### 3. Memory Management
- **Stack-based**: Local variables on stack
- **Garbage Collection**: Automatic memory management
- **Property Tables**: Efficient property storage

#### 4. Game-Specific Constructs
- **Room System**: Specialized object type for locations
- **Inventory Management**: Built-in containment system
- **Parser Integration**: Direct verb-to-routine mapping
- **Event Scheduling**: Built-in time management

### MDL Heritage Features

#### 1. LISP-like Structure
- **S-expressions**: Nested list structure
- **Functional Elements**: Some functional programming concepts
- **Dynamic Typing**: Runtime type checking

#### 2. Differences from Pure LISP
- **No cons/car/cdr**: Traditional LISP list operations absent
- **Imperative Style**: More procedural than functional
- **Static Compilation**: Compiled rather than interpreted

## Dependency Analysis

### Internal Dependencies

#### Core Engine Dependencies
1. **Parser → Verbs**: Parser calls verb routines
2. **Verbs → Objects**: Verbs operate on objects
3. **Objects → Actions**: Objects have action routines
4. **Clock → Demons**: Time system triggers events
5. **People → Clock**: NPCs scheduled by time system

#### Data Dependencies
1. **Rooms → Vocabulary**: Room names in parser vocabulary
2. **Items → Properties**: Items depend on property system
3. **Syntax → Parser**: Grammar rules used by parser
4. **Globals → All Modules**: Global state accessed everywhere

### External Dependencies (Original System)

#### Development Environment
- **TOPS20 Operating System**: Original development platform
- **ZILCH Compiler**: ZIL to Z-code compiler
- **MDL Runtime**: Base language support
- **File System**: Source code and data file management

#### Runtime Dependencies
- **Z-machine Interpreter**: Virtual machine for execution
- **Memory Management**: Stack and heap allocation
- **I/O System**: Console input/output handling
- **Save System**: Game state persistence

## Platform-Specific Code Patterns

### Z-machine Specific Features

#### 1. Memory Constraints
- **Object Table Limits**: Maximum number of objects
- **Property Size Limits**: Property value size restrictions
- **Stack Size**: Limited call stack depth
- **String Pool**: Shared string storage

#### 2. Bytecode Generation
- **Instruction Set**: Z-machine opcodes
- **Branching**: Conditional jump instructions
- **Property Access**: Specialized property instructions
- **Object Manipulation**: Object tree operations

### File Structure Patterns

#### 1. Modular Organization
```
DEADLINE/
├── DEADLINE.ZIL     (Main game file)
├── PARSER.ZIL       (Command parsing)
├── VERBS.ZIL        (Verb implementations)
├── OBJECTS.ZIL      (Object definitions)
├── ROOMS.ZIL        (Location definitions)
├── PEOPLE.ZIL       (Character behaviors)
├── CLOCK.ZIL        (Time management)
├── GLOBALS.ZIL      (Global variables)
├── VOCAB.ZIL        (Vocabulary definitions)
└── DEBUG.ZIL        (Development utilities)
```

#### 2. Inclusion System
- **INCLUDE directives**: File inclusion mechanism
- **Compilation Order**: Dependencies resolved at compile time
- **Symbol Resolution**: Cross-file symbol references

## Third-Party Libraries and Components

### Original System Libraries
- **MDL Standard Library**: Base language functions
- **Z-machine Runtime**: Virtual machine support
- **System Libraries**: OS-specific functionality

### Modern Python Equivalents Needed
- **Standard Library Modules**:
  - `sys` - System functionality
  - `os` - Operating system interface
  - `re` - Regular expressions for parsing
  - `pickle` - Save game serialization
  - `json` - Configuration and data files
  - `argparse` - Command line argument parsing
  - `logging` - Debug and error logging
  - `datetime` - Time management
  - `random` - Random number generation

## Code Architecture Patterns

### 1. Command Pattern Implementation
- **Verb Handlers**: Each verb has dedicated routine
- **Object Actions**: Objects can override default behaviors
- **Parser Integration**: Direct verb-to-function mapping

### 2. State Machine Patterns
- **Game States**: Different game modes (play, inventory, etc.)
- **Character States**: NPC behavior state transitions
- **Object States**: Items can change properties over time

### 3. Observer Pattern
- **Event System**: Objects can respond to events
- **Time Events**: Scheduled actions trigger updates
- **Player Actions**: Actions can trigger cascading events

### 4. Factory Pattern
- **Object Creation**: Consistent object initialization
- **Room Generation**: Standard room setup procedures
- **Character Instantiation**: NPC creation with default behaviors

## Complexity Assessment

### High Complexity Areas
1. **Parser System**: Natural language processing
2. **Time Management**: Event scheduling and synchronization
3. **NPC Behavior**: Complex character interaction logic
4. **Save/Restore**: Game state serialization

### Medium Complexity Areas
1. **Object System**: Property management and hierarchy
2. **Verb Implementations**: Command processing logic
3. **Room Navigation**: Geography and movement system

### Low Complexity Areas
1. **Vocabulary**: Word-to-ID mapping
2. **Basic Actions**: Simple verb implementations
3. **Text Output**: Description display system

This inventory forms the foundation for understanding the scope and complexity of the porting task, identifying the key areas that will require careful translation from ZIL's unique constructs to Python's object-oriented paradigms.