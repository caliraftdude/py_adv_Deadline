# 7_code_translation/src/deadline/data/__init__.py
"""
Game data module - provides access to game content files
"""

import json
from pathlib import Path
from typing import Dict, Any, List

# Get the data directory path
DATA_DIR = Path(__file__).parent


def load_game_data() -> Dict[str, Any]:
    """Load the main game data file"""
    with open(DATA_DIR / "game_data.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def load_vocabulary() -> Dict[str, Any]:
    """Load the vocabulary data"""
    with open(DATA_DIR / "vocabulary.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def load_syntax_rules() -> List[Dict[str, Any]]:
    """Load the syntax rules"""
    with open(DATA_DIR / "syntax_rules.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def load_schedules() -> Dict[str, Any]:
    """Load the schedule data"""
    with open(DATA_DIR / "schedules.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def get_data_path() -> Path:
    """Get the path to the data directory"""
    return DATA_DIR


__all__ = [
    'load_game_data',
    'load_vocabulary',
    'load_syntax_rules',
    'load_schedules',
    'get_data_path',
    'DATA_DIR'
]