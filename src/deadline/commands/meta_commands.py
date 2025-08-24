# 7_code_translation/src/deadline/commands/meta_commands.py
"""
Meta commands - save, load, quit, inventory, etc.
"""
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from ..parser.parser import ParseResult
    
from .base_command import Command, CommandResult, CommandStatus
from ..core.game_engine import GameState


class SaveCommand(Command):
    """Save the game - equivalent to V-SAVE"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        # Get filename if provided
        filename = parse_result.text if parse_result.text else None
        
        try:
            success = self.engine.save_game(filename)
            if success:
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message="Game saved.",
                    consumed_time=False
                )
            else:
                return CommandResult(
                    status=CommandStatus.FAILURE,
                    message="Failed to save game.",
                    consumed_time=False
                )
        except Exception as e:
            return CommandResult(
                status=CommandStatus.ERROR,
                message=f"Save error: {e}",
                consumed_time=False
            )


class LoadCommand(Command):
    """Load/restore a saved game - equivalent to V-RESTORE"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        # Get filename if provided
        filename = parse_result.text if parse_result.text else None
        
        if not filename:
            # List available saves
            saves = self.engine.save_manager.list_saves()
            if saves:
                save_list = "\n".join([f"  - {s['filename']}" for s in saves])
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=f"Available saves:\n{save_list}\n\nUse 'load [filename]' to load.",
                    consumed_time=False
                )
            else:
                return CommandResult(
                    status=CommandStatus.FAILURE,
                    message="No saved games found.",
                    consumed_time=False
                )
        
        try:
            success = self.engine.load_game(filename)
            if success:
                # Redisplay current room
                current_room = self.world.get_current_room()
                if current_room:
                    from ..io.interface import GameInterface
                    interface = GameInterface(self.engine)
                    interface.display_room(current_room)
                
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message="Game loaded.",
                    consumed_time=False,
                    update_state=False  # Don't update state after load
                )
            else:
                return CommandResult(
                    status=CommandStatus.FAILURE,
                    message="Failed to load game.",
                    consumed_time=False
                )
        except Exception as e:
            return CommandResult(
                status=CommandStatus.ERROR,
                message=f"Load error: {e}",
                consumed_time=False
            )


class QuitCommand(Command):
    """Quit the game - equivalent to V-QUIT"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        # Confirm quit
        from ..io.interface import GameInterface
        interface = GameInterface(self.engine)
        
        if interface.confirm("Are you sure you want to quit?"):
            self.engine.state = GameState.QUIT
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message="",
                consumed_time=False,
                update_state=False
            )
        else:
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message="Continuing game.",
                consumed_time=False
            )


class InventoryCommand(Command):
    """Show inventory - equivalent to V-INVENTORY"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        inventory = self.player.get_inventory()
        
        if not inventory:
            message = "You are carrying nothing."
        else:
            items = []
            for item in inventory:
                items.append(f"  {item.get_inventory_description()}")
            message = "You are carrying:\n" + "\n".join(items)
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=message,
            consumed_time=False
        )


class ScoreCommand(Command):
    """Show score - equivalent to V-SCORE"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        score = self.engine.score
        max_score = self.engine.config.max_score
        moves = self.engine.moves
        
        message = f"Your score is {score} out of {max_score} in {moves} moves."
        
        # Add evidence count
        evidence_count = self.world.evidence_manager.get_evidence_count()
        if evidence_count > 0:
            message += f"\nYou have collected {evidence_count} pieces of evidence."
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=message,
            consumed_time=False
        )


class WaitCommand(Command):
    """Wait/pass time - equivalent to V-WAIT"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        # Check for specific wait duration
        if parse_result.text:
            try:
                # Parse duration (e.g., "10 minutes", "1 hour")
                duration_text = parse_result.text.lower()
                if "hour" in duration_text:
                    hours = int(duration_text.split()[0])
                    minutes = hours * 60
                elif "minute" in duration_text:
                    minutes = int(duration_text.split()[0])
                else:
                    minutes = int(duration_text)
                
                self.engine.time_manager.wait_for_duration(minutes)
                message = f"You wait for {minutes} minutes."
                
            except:
                # Default wait
                minutes = 3
                self.engine.time_manager.wait_for_duration(minutes)
                message = "Time passes..."
        else:
            # Default wait is 3 minutes
            minutes = 3
            self.engine.time_manager.wait_for_duration(minutes)
            message = "Time passes..."
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=message,
            consumed_time=False  # Time already advanced
        )


class HelpCommand(Command):
    """Show help - equivalent to V-HELP"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        help_text = """
DEADLINE - Command Reference

Movement:
  GO [direction] or just [direction] - Move in a direction
  ENTER [object] - Enter something
  EXIT - Leave current location

Examination:
  LOOK or L - Look around
  EXAMINE [object] or X [object] - Examine something closely
  SEARCH [object] - Search something thoroughly
  READ [object] - Read something
  LOOK UNDER/BEHIND [object] - Look under or behind something

Manipulation:
  TAKE/GET [object] - Pick up an object
  DROP [object] - Drop an object
  OPEN/CLOSE [object] - Open or close something
  LOCK/UNLOCK [object] WITH [key] - Lock or unlock something
  PUT [object] IN/ON [container] - Put object in/on something

Communication:
  TALK TO [person] - Talk to someone
  ASK [person] ABOUT [topic] - Ask about something
  TELL [person] ABOUT [topic] - Tell someone something
  SHOW [object] TO [person] - Show something to someone
  ACCUSE [person] - Accuse someone of murder

Meta Commands:
  INVENTORY or I - Show what you're carrying
  SCORE - Show your score
  SAVE [filename] - Save the game
  LOAD/RESTORE [filename] - Load a saved game
  WAIT [minutes] - Wait for time to pass
  QUIT - Quit the game
  HELP - Show this help

Tips:
- Examine everything carefully for clues
- Talk to everyone and ask about suspicious topics
- Time passes with each action - NPCs follow schedules
- Collect evidence before making an accusation
- Save your game frequently
        """
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=help_text.strip(),
            consumed_time=False
        )


class AnalyzeCommand(Command):
    """Analyze evidence - Deadline specific command"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        obj = self.get_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="You don't have that to analyze."
            )
        
        # Check if it's evidence
        if not obj.get_property('evidence'):
            return CommandResult(
                status=CommandStatus.FAILURE,
                message=f"The {obj.name} doesn't seem relevant to the case."
            )
        
        # Simulate sending to lab (Sergeant Duffy)
        analysis = obj.get_property('analysis_result')
        if analysis:
            # Mark as analyzed
            obj.set_property('analyzed', True)
            self.world.evidence_manager.collect_evidence(f"{obj.id}_analysis")
            
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"You send the {obj.name} to Sergeant Duffy for analysis.\n\n" +
                       f"After a few minutes, the results come back:\n{analysis}"
            )
        else:
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"The {obj.name} doesn't reveal anything unusual under analysis."
            )


class FingerprintCommand(Command):
    """Check for fingerprints - Deadline specific"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        obj = self.get_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see that here."
            )
        
        # Check for fingerprints
        fingerprints = obj.get_property('fingerprints', [])
        if fingerprints:
            names = ", ".join(fingerprints)
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"Dusting the {obj.name} for fingerprints reveals: {names}"
            )
        else:
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"No clear fingerprints can be found on the {obj.name}."
            )