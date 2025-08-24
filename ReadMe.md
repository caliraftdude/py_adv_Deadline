## Directory Structure

```
7_code_translation/
├── X requirements.txt
├── X setup.py
├── README.md
├── src/
│   └── deadline/
│       ├── X __init__.py
│       ├── X main.py
│       ├── core/
│       │   ├── X __init__.py
│       │   ├── X game_engine.py
│       │   ├── X game_object.py
│       │   ├── X property_system.py
│       │   ├── X container_system.py
│       │   ├── X flags.py
│       │   └── X exceptions.py
│       ├── parser/
│       │   ├── X __init__.py
│       │   ├── X parser.py
│       │   ├── X vocabulary.py
│       │   ├── X syntax.py
│       │   └── X disambiguator.py
│       ├── commands/
│       │   ├── X __init__.py
│       │   ├── X base_command.py
│       │   ├── X movement.py
│       │   ├── X manipulation.py
│       │   ├── X examination.py
│       │   ├── X communication.py
│       │   └── X meta_commands.py
│       ├── world/
│       │   ├── X __init__.py
│       │   ├── X world_manager.py
│       │   ├── X room_manager.py
│       │   ├── X character_manager.py
│       │   └── X evidence_manager.py
│       ├── time/
│       │   ├── X __init__.py
│       │   ├── X time_manager.py
│       │   ├── X scheduler.py
│       │   └── X events.py
│       ├── io/
│       │   ├── X __init__.py
│       │   ├── X interface.py
│       │   ├── X save_system.py
│       │   └── X output_formatter.py
│       └── data/
│           ├── X __init__.py
│           ├── X game_data.json
│           ├── X vocabulary.json
│           ├── X syntax_rules.json
│           └── X schedules.json
├── tests/
│   ├── X __init__.py
│   ├── X test_parser.py
│   ├── X test_commands.py
│   ├── X test_world.py
│   └── X test_game.py
└── docs/
    ├── X README.md
    └── X DESIGN.md
```