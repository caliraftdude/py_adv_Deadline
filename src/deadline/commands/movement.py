# 7_code_translation/src/deadline/commands/movement.py
"""
Movement commands - navigation through the game world
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..parser.parser import ParseResult
    
from .base_command import Command, CommandResult, CommandStatus
from ..core.flags import ObjectFlag


class GoCommand(Command):
    """Go in a direction - equivalent to V-WALK"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        direction = parse_result.direct_object
        
        # Normalize direction
        direction_map = {
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
            'ne': 'northeast', 'nw': 'northwest', 'se': 'southeast', 'sw': 'southwest',
            'u': 'up', 'd': 'down'
        }
        
        direction = direction_map.get(direction, direction)
        
        # Try to move
        success, message = self.world.move_player(direction)
        
        if success:
            # Get new room description
            new_room = self.world.get_current_room()
            if new_room:
                # Build room description
                from ..io.interface import GameInterface
                interface = GameInterface(self.engine)
                interface.display_room(new_room)
                
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=""  # Room already displayed
                )
        
        return CommandResult(
            status=CommandStatus.FAILURE,
            message=message or "You can't go that way."
        )


class EnterCommand(Command):
    """Enter something - equivalent to V-ENTER"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        if parse_result.direct_object:
            # Try to enter a specific object
            obj = self.get_object(parse_result.direct_object)
            if not obj:
                return CommandResult(
                    status=CommandStatus.ERROR,
                    message="I don't see that here."
                )
            
            if obj.has_flag(ObjectFlag.VEHICLE) or obj.has_flag(ObjectFlag.CONTAINER):
                if obj.has_flag(ObjectFlag.OPEN) or not obj.has_flag(ObjectFlag.CONTAINER):
                    # Enter the object
                    self.player.move_to(obj)
                    return CommandResult(
                        status=CommandStatus.SUCCESS,
                        message=f"You enter the {obj.name}."
                    )
                else:
                    return CommandResult(
                        status=CommandStatus.FAILURE,
                        message=f"The {obj.name} is closed."
                    )
            else:
                return CommandResult(
                    status=CommandStatus.FAILURE,
                    message=f"You can't enter the {obj.name}."
                )
        else:
            # Generic enter - try to go "in"
            return GoCommand(self.engine).execute(
                type('ParseResult', (), {'direct_object': 'in'})()
            )


class ExitCommand(Command):
    """Exit/leave current location - equivalent to V-EXIT"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        # Check if player is in a vehicle/container
        current_location = self.player.location
        
        if current_location and current_location != self.world.get_current_room():
            # Player is in something, exit it
            parent_location = current_location.location
            if parent_location:
                self.player.move_to(parent_location)
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=f"You exit the {current_location.name}."
                )
        
        # Try to go "out"
        return GoCommand(self.engine).execute(
            type('ParseResult', (), {'direct_object': 'out'})()
        )