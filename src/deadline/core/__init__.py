# 7_code_translation/src/deadline/core/__init__.py
"""
Core game engine and object system
"""

from .game_engine import GameEngine, GameState, GameConfig
from .game_object import (
    GameObject, 
    Room, 
    Item, 
    Container, 
    Character, 
    Player
)
from .flags import ObjectFlag
from .property_system import PropertyManager
from .container_system import ContainerSystem
from .exceptions import (
    GameException,
    ParserException,
    CommandException,
    SaveLoadException,
    InvalidStateException,
    TimeException
)

__all__ = [
    # Engine
    'GameEngine',
    'GameState', 
    'GameConfig',
    
    # Objects
    'GameObject',
    'Room',
    'Item',
    'Container',
    'Character',
    'Player',
    
    # Systems
    'ObjectFlag',
    'PropertyManager',
    'ContainerSystem',
    
    # Exceptions
    'GameException',
    'ParserException',
    'CommandException',
    'SaveLoadException',
    'InvalidStateException',
    'TimeException'
]
