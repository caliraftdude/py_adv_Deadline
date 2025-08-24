# 7_code_translation/src/deadline/core/exceptions.py
"""
Custom exceptions for the game engine
"""

class GameException(Exception):
    """Base exception for game-related errors"""
    pass

class ParserException(GameException):
    """Exception raised during parsing"""
    pass

class CommandException(GameException):
    """Exception raised during command execution"""
    pass

class SaveLoadException(GameException):
    """Exception raised during save/load operations"""
    pass

class InvalidStateException(GameException):
    """Exception raised when game state is invalid"""
    pass

class TimeException(GameException):
    """Exception raised for time-related errors"""
    pass