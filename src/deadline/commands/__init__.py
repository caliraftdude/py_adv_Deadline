# 7_code_translation/src/deadline/commands/__init__.py
"""
Command processing system for game actions
"""

from .base_command import (
    Command,
    CommandProcessor,
    CommandResult,
    CommandStatus
)

# Movement commands
from .movement import (
    GoCommand,
    EnterCommand,
    ExitCommand
)

# Manipulation commands
from .manipulation import (
    TakeCommand,
    DropCommand,
    OpenCommand,
    CloseCommand,
    LockCommand,
    UnlockCommand,
    PutCommand,
    GiveCommand
)

# Examination commands
from .examination import (
    LookCommand,
    ExamineCommand,
    SearchCommand,
    ReadCommand,
    LookUnderCommand,
    LookBehindCommand
)

# Communication commands
from .communication import (
    TalkCommand,
    AskCommand,
    TellCommand,
    ShowCommand,
    AccuseCommand,
    ArrestCommand
)

# Meta commands
from .meta_commands import (
    SaveCommand,
    LoadCommand,
    QuitCommand,
    InventoryCommand,
    ScoreCommand,
    WaitCommand,
    HelpCommand,
    AnalyzeCommand,
    FingerprintCommand
)

__all__ = [
    # Base
    'Command',
    'CommandProcessor',
    'CommandResult',
    'CommandStatus',
    
    # Movement
    'GoCommand',
    'EnterCommand',
    'ExitCommand',
    
    # Manipulation
    'TakeCommand',
    'DropCommand',
    'OpenCommand',
    'CloseCommand',
    'LockCommand',
    'UnlockCommand',
    'PutCommand',
    'GiveCommand',
    
    # Examination
    'LookCommand',
    'ExamineCommand',
    'SearchCommand',
    'ReadCommand',
    'LookUnderCommand',
    'LookBehindCommand',
    
    # Communication
    'TalkCommand',
    'AskCommand',
    'TellCommand',
    'ShowCommand',
    'AccuseCommand',
    'ArrestCommand',
    
    # Meta
    'SaveCommand',
    'LoadCommand',
    'QuitCommand',
    'InventoryCommand',
    'ScoreCommand',
    'WaitCommand',
    'HelpCommand',
    'AnalyzeCommand',
    'FingerprintCommand'
]