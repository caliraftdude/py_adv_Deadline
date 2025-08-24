"""
Deadline Interactive Fiction
A Python 3.13 port of the classic Infocom game
"""

__version__ = "1.0.0"
__author__ = "Marc Blank (original), Python Port Team"
__license__ = "MIT"

from .core.game_engine import GameEngine
from .core.game_object import GameObject, Room, Item, Character
from .parser.parser import GameParser

__all__ = [
    "GameEngine",
    "GameObject", 
    "Room",
    "Item",
    "Character",
    "GameParser",
]