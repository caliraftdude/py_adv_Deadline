# 7_code_translation/README.md

# Deadline - Python 3.13 Port

A complete port of the classic 1982 Infocom interactive fiction game "Deadline" by Marc Blank, translated from ZIL (Zork Implementation Language) to Python 3.13.

## Installation

### Requirements
- Python 3.13 or higher
- pip package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd 7_code_translation

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the game
pip install -e .
```

## Running the Game

### From command line:
```bash
# Run directly
python -m deadline.main

# Or if installed
deadline
```

### Command line options:
```bash
deadline --help              # Show help
deadline --debug             # Enable debug mode
deadline --load savefile     # Load a saved game
deadline --data-path ./data  # Specify custom data directory
```

## How to Play

You are a police detective investigating the apparent suicide of wealthy industrialist Marshall Robner. You have 12 hours to gather evidence and solve the case.

### Basic Commands
- **Movement**: `north`, `south`, `east`, `west`, `up`, `down` (or `n`, `s`, `e`, `w`, `u`, `d`)
- **Examine**: `examine [object]` or `x [object]`
- **Take/Drop**: `take [object]`, `drop [object]`
- **Inventory**: `inventory` or `i`
- **Talk**: `talk to [person]`, `ask [person] about [topic]`
- **Accuse**: `accuse [person] of murder`

### Game Features
- Real-time clock (each action advances time)
- NPCs follow schedules and move around
- Evidence collection system
- Multiple solution paths
- Save/restore functionality

### Tips
1. Examine everything carefully
2. Talk to all characters about various topics
3. Take notes - the game doesn't track clues for you
4. Pay attention to the time - events happen on schedule
5. Save frequently

## Project Structure

```
7_code_translation/
├── src/
│   └── deadline/
│       ├── core/          # Core game engine
│       ├── parser/        # Natural language parser
│       ├── commands/      # Command implementations
│       ├── world/         # World and object management
│       ├── time/          # Time and event system
│       ├── io/            # Input/output handling
│       └── data/          # Game data (JSON files)
├── tests/                 # Test suite
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
└── README.md             # This file
```

## Architecture

The game uses a data-driven architecture:
- **Game Engine**: Generic, reusable interactive fiction engine
- **Game Data**: All content stored in JSON files
- **Parser**: Natural language processing for commands
- **World Manager**: Manages game state and object relationships
- **Time System**: Handles scheduled events and NPC behaviors

## Testing

Run the test suite:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=deadline --cov-report=html

# Run specific test module
pytest tests/test_parser.py -v
```

## Development

### Adding Content
All game content is in JSON files in `src/deadline/data/`:
- `game_data.json`: Rooms, objects, characters, and game configuration
- `vocabulary.json`: Parser vocabulary
- `syntax_rules.json`: Command patterns
- `schedules.json`: Time-based events

### Creating New Games
This engine can run other interactive fiction games:
1. Replace the JSON data files with your content
2. Adjust configuration in `game_data.json`
3. Add custom commands if needed

### Code Style
```bash
# Format code
black src/ tests/

# Check types
mypy src/deadline

# Lint
flake8 src/ tests/
```

## Troubleshooting

### Common Issues

**ImportError on startup**
- Ensure Python 3.13+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`

**Game data not loading**
- Verify data files exist in `src/deadline/data/`
- Check JSON syntax is valid

**Save/Load not working**
- Ensure write permissions in home directory
- Check `~/.deadline_saves/` directory exists

## Credits

- **Original Game**: Marc Blank (Infocom, 1982)
- **Python Port**: [Your Name]
- **Based on**: ZIL source code from historical archives

## License

This port is for educational and preservation purposes. The original game and story are property of Activision (current rights holder of Infocom properties).

## Resources

- [Original Deadline Information](https://en.wikipedia.org/wiki/Deadline_(video_game))
- [Interactive Fiction Database](https://ifdb.org)
- [ZIL Documentation](https://github.com/ZoBoRf/ZILF)