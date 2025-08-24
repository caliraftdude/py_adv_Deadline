# 7_code_translation/src/deadline/commands/base_command.py
"""
Base command classes and command processor
Translated from ZIL verb handling system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TYPE_CHECKING, List
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

if TYPE_CHECKING:
    from ..core.game_engine import GameEngine
    from ..core.game_object import GameObject
    from ..parser.parser import ParseResult

logger = logging.getLogger(__name__)


class CommandStatus(Enum):
    """Command execution status"""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    PARTIAL = "partial"
    QUIT = "quit"
    RESTART = "restart"


@dataclass
class CommandResult:
    """Result of command execution"""
    status: CommandStatus
    message: str
    consumed_time: bool = True
    update_state: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(cls, message: str, **kwargs) -> 'CommandResult':
        """Create a success result"""
        return cls(status=CommandStatus.SUCCESS, message=message, **kwargs)
    
    @classmethod
    def failure(cls, message: str, **kwargs) -> 'CommandResult':
        """Create a failure result"""
        return cls(status=CommandStatus.FAILURE, message=message, **kwargs)
    
    @classmethod
    def error(cls, message: str, **kwargs) -> 'CommandResult':
        """Create an error result"""
        return cls(status=CommandStatus.ERROR, message=message, **kwargs)


class Command(ABC):
    """
    Abstract base class for all commands
    Equivalent to ZIL verb routines
    """
    
    def __init__(self, engine: 'GameEngine'):
        self.engine = engine
        self.world = engine.world_manager if hasattr(engine, 'world_manager') else None
        self.player = self.world.player if self.world else None
        
    @abstractmethod
    def execute(self, parse_result: 'ParseResult') -> CommandResult:
        """Execute the command"""
        pass
    
    def can_execute(self, parse_result: 'ParseResult') -> bool:
        """Check if command can be executed - default implementation"""
        return True
    
    def get_object(self, obj_ref: str) -> Optional['GameObject']:
        """Resolve object reference to actual object"""
        if not obj_ref or not self.world:
            return None
        
        # Try to find object in current room or inventory
        return self.world.find_object(obj_ref)
    
    def get_current_room(self):
        """Get the current room"""
        if self.world:
            return self.world.get_current_room()
        return None
    
    def format_message(self, template: str, **kwargs) -> str:
        """Format a message with variable substitution"""
        return template.format(**kwargs)
    
    def is_dark(self) -> bool:
        """Check if current location is dark"""
        room = self.get_current_room()
        return room.is_dark() if room else False
    
    def require_light(self) -> bool:
        """Check if command requires light"""
        return True  # Most commands need light; override for exceptions


class CommandProcessor:
    """
    Central command processing system
    Routes parsed commands to appropriate handlers
    """
    
    def __init__(self, engine: 'GameEngine'):
        self.engine = engine
        self.commands: Dict[str, Command] = {}
        self.command_aliases: Dict[str, str] = {}
        self._register_commands()
        
        # Track command history
        self.command_history: List[str] = []
        self.max_history = 100
    
    def _register_commands(self):
        """Register all available commands"""
        # Import here to avoid circular dependencies
        from .movement import GoCommand, EnterCommand, ExitCommand
        from .manipulation import (TakeCommand, DropCommand, OpenCommand, 
                                 CloseCommand, LockCommand, UnlockCommand,
                                 PutCommand, GiveCommand)
        from .examination import LookCommand, ExamineCommand, SearchCommand, ReadCommand
        from .communication import TalkCommand, AskCommand, TellCommand, AccuseCommand
        from .meta_commands import (SaveCommand, LoadCommand, QuitCommand, 
                                   InventoryCommand, ScoreCommand, WaitCommand,
                                   HelpCommand, AboutCommand)
        
        # Movement commands
        self.register_command('go', GoCommand(self.engine))
        self.register_command('enter', EnterCommand(self.engine))
        self.register_command('exit', ExitCommand(self.engine))
        
        # Manipulation commands
        take_cmd = TakeCommand(self.engine)
        self.register_command('take', take_cmd)
        self.register_command('get', take_cmd)  # Alias
        self.register_command('pick', take_cmd)  # Alias for "pick up"
        
        self.register_command('drop', DropCommand(self.engine))
        self.register_command('open', OpenCommand(self.engine))
        self.register_command('close', CloseCommand(self.engine))
        self.register_command('lock', LockCommand(self.engine))
        self.register_command('unlock', UnlockCommand(self.engine))
        self.register_command('put', PutCommand(self.engine))
        self.register_command('give', GiveCommand(self.engine))
        
        # Examination commands
        look_cmd = LookCommand(self.engine)
        self.register_command('look', look_cmd)
        self.register_command('l', look_cmd)  # Shortcut
        
        examine_cmd = ExamineCommand(self.engine)
        self.register_command('examine', examine_cmd)
        self.register_command('x', examine_cmd)  # Shortcut
        self.register_command('inspect', examine_cmd)  # Alias
        
        self.register_command('search', SearchCommand(self.engine))
        self.register_command('read', ReadCommand(self.engine))
        
        # Communication commands
        self.register_command('talk', TalkCommand(self.engine))
        self.register_command('ask', AskCommand(self.engine))
        self.register_command('tell', TellCommand(self.engine))
        self.register_command('accuse', AccuseCommand(self.engine))
        
        # Meta commands
        self.register_command('save', SaveCommand(self.engine))
        
        load_cmd = LoadCommand(self.engine)
        self.register_command('load', load_cmd)
        self.register_command('restore', load_cmd)  # Alias
        
        self.register_command('quit', QuitCommand(self.engine))
        
        inventory_cmd = InventoryCommand(self.engine)
        self.register_command('inventory', inventory_cmd)
        self.register_command('i', inventory_cmd)  # Shortcut
        
        self.register_command('score', ScoreCommand(self.engine))
        
        wait_cmd = WaitCommand(self.engine)
        self.register_command('wait', wait_cmd)
        self.register_command('z', wait_cmd)  # Shortcut
        
        self.register_command('help', HelpCommand(self.engine))
        self.register_command('about', AboutCommand(self.engine))
    
    def register_command(self, verb: str, command: Command):
        """Register a command handler for a verb"""
        self.commands[verb.lower()] = command
    
    def register_alias(self, alias: str, verb: str):
        """Register an alias for a verb"""
        self.command_aliases[alias.lower()] = verb.lower()
    
    def get_command(self, verb: str) -> Optional[Command]:
        """Get command handler for a verb"""
        verb_lower = verb.lower()
        
        # Check for alias
        if verb_lower in self.command_aliases:
            verb_lower = self.command_aliases[verb_lower]
        
        return self.commands.get(verb_lower)
    
    def execute(self, parse_result: 'ParseResult') -> CommandResult:
        """
        Execute a parsed command
        
        Args:
            parse_result: Parsed command from parser
            
        Returns:
            CommandResult with execution results
        """
        # Add to history
        if parse_result.raw_input:
            self._add_to_history(parse_result.raw_input)
        
        # Check if parse was successful
        if not parse_result.is_valid:
            return CommandResult.error(
                parse_result.error_message or "I don't understand that command."
            )
        
        # Get command handler
        verb = parse_result.verb
        if not verb:
            return CommandResult.error("No verb found in command.")
        
        command = self.get_command(verb)
        
        if not command:
            # Try to give a helpful message
            similar = self._find_similar_commands(verb)
            if similar:
                return CommandResult.error(
                    f"I don't know how to '{verb}'. Did you mean '{similar[0]}'?"
                )
            return CommandResult.error(f"I don't know how to '{verb}'.")
        
        # Check if command can be executed
        try:
            if not command.can_execute(parse_result):
                return CommandResult.failure("You can't do that right now.")
        except Exception as e:
            logger.warning(f"Error checking can_execute for {verb}: {e}")
            # Continue anyway
        
        # Check for darkness (most commands need light)
        if hasattr(command, 'require_light') and command.require_light():
            if hasattr(command, 'is_dark') and command.is_dark():
                return CommandResult.failure(
                    "It's too dark to see anything here. You need a light source."
                )
        
        # Execute command
        try:
            result = command.execute(parse_result)
            
            # Ensure we have a valid result
            if not isinstance(result, CommandResult):
                logger.error(f"Command {verb} did not return CommandResult")
                return CommandResult.error("Internal error executing command.")
            
            return result
            
        except NotImplementedError:
            return CommandResult.error(
                f"The '{verb}' command is not yet implemented."
            )
        except Exception as e:
            logger.error(f"Command execution error for {verb}: {e}", exc_info=True)
            return CommandResult.error(
                "An error occurred while executing that command."
            )
    
    def _add_to_history(self, command: str):
        """Add command to history"""
        self.command_history.append(command)
        
        # Limit history size
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
    
    def _find_similar_commands(self, verb: str) -> List[str]:
        """Find commands similar to the given verb"""
        similar = []
        verb_lower = verb.lower()
        
        # Check for commands that start with the same letter
        for cmd in self.commands:
            if cmd.startswith(verb_lower[0]):
                similar.append(cmd)
        
        # Check for commands with similar length
        for cmd in self.commands:
            if abs(len(cmd) - len(verb_lower)) <= 2:
                if cmd not in similar:
                    similar.append(cmd)
        
        return similar[:3]  # Return top 3 suggestions
    
    def get_available_commands(self) -> List[str]:
        """Get list of all available commands"""
        commands = list(self.commands.keys())
        commands.extend(self.command_aliases.keys())
        return sorted(set(commands))
    
    def get_command_help(self, verb: str = None) -> str:
        """Get help text for a command or all commands"""
        if verb:
            command = self.get_command(verb)
            if command:
                # Get help from command if it has a help method
                if hasattr(command, 'get_help'):
                    return command.get_help()
                else:
                    return f"The '{verb}' command is available but has no specific help."
            else:
                return f"Unknown command: '{verb}'"
        else:
            # Return general help
            commands = self.get_available_commands()
            help_text = "Available commands:\n"
            help_text += ", ".join(commands)
            help_text += "\n\nType 'help [command]' for specific command help."
            return help_text
    
    def get_history(self, count: int = 10) -> List[str]:
        """Get recent command history"""
        return self.command_history[-count:]


class MetaCommand(Command):
    """Base class for meta-commands that don't affect game state"""
    
    def __init__(self, engine: 'GameEngine'):
        super().__init__(engine)
    
    def require_light(self) -> bool:
        """Meta-commands don't require light"""
        return False


class MovementCommand(Command):
    """Base class for movement commands"""
    
    def __init__(self, engine: 'GameEngine'):
        super().__init__(engine)
    
    def can_move(self, direction: str) -> bool:
        """Check if movement is possible in a direction"""
        if not self.world:
            return False
        
        room = self.get_current_room()
        if not room:
            return False
        
        # Check if exit exists
        exit_room = room.get_exit(direction)
        return exit_room is not None
    
    def move_player(self, direction: str) -> CommandResult:
        """Move player in a direction"""
        if not self.world:
            return CommandResult.error("Game world not initialized.")
        
        room = self.get_current_room()
        if not room:
            return CommandResult.error("You're nowhere!")
        
        # Check for exit
        exit_room_id = room.get_exit(direction)
        if not exit_room_id:
            return CommandResult.failure("You can't go that way.")
        
        # Get the destination room
        new_room = self.world.get_room(exit_room_id)
        if not new_room:
            return CommandResult.error(f"Destination room '{exit_room_id}' not found.")
        
        # Move the player
        if self.player:
            self.player.move_to(new_room)
        
        # Set current room in world
        self.world.current_room = new_room
        
        # Mark room as visited
        from ..core.game_object import ObjectFlag
        new_room.set_flag(ObjectFlag.VISITED)
        
        # Return success with room description
        description = new_room.get_room_description()
        
        # Add exits to description
        exits = new_room.get_available_exits()
        if exits:
            description += f"\n\nExits: {', '.join(exits)}"
        
        # List visible objects
        visible_items = [obj for obj in new_room.contents 
                        if obj != self.player and obj.is_visible()]
        if visible_items:
            description += "\n\nYou can see:"
            for item in visible_items:
                description += f"\n  {item.get_inventory_description()}"
        
        return CommandResult.success(description)


class ManipulationCommand(Command):
    """Base class for object manipulation commands"""
    
    def __init__(self, engine: 'GameEngine'):
        super().__init__(engine)
    
    def get_held_object(self, obj_ref: str) -> Optional['GameObject']:
        """Get an object from player's inventory"""
        if not obj_ref or not self.player:
            return None
        
        # Search player's inventory
        for obj in self.player.contents:
            if obj.id == obj_ref or obj.name.lower() == obj_ref.lower():
                return obj
            # Check synonyms
            if hasattr(obj, 'synonyms'):
                if obj_ref.lower() in [s.lower() for s in obj.synonyms]:
                    return obj
        
        return None
    
    def get_room_object(self, obj_ref: str) -> Optional['GameObject']:
        """Get an object from the current room"""
        room = self.get_current_room()
        if not room or not obj_ref:
            return None
        
        # Search room contents
        for obj in room.contents:
            if obj == self.player:
                continue
            if obj.id == obj_ref or obj.name.lower() == obj_ref.lower():
                return obj
            # Check synonyms
            if hasattr(obj, 'synonyms'):
                if obj_ref.lower() in [s.lower() for s in obj.synonyms]:
                    return obj
        
        return None
    
    def get_visible_object(self, obj_ref: str) -> Optional['GameObject']:
        """Get a visible object (in room or inventory)"""
        # Check inventory first
        obj = self.get_held_object(obj_ref)
        if obj:
            return obj
        
        # Check room
        return self.get_room_object(obj_ref)


# Specific command implementations would go in their respective files
# This file provides the base infrastructure for all commands