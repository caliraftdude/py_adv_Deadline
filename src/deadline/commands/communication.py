# 7_code_translation/src/deadline/commands/communication.py
"""
Communication commands - talking to NPCs and making accusations
"""
from typing import TYPE_CHECKING
from ..core.game_engine import GameState
if TYPE_CHECKING:
    from ..parser.parser import ParseResult

from .base_command import Command, CommandResult, CommandStatus
from ..core.flags import ObjectFlag


class TalkCommand(Command):
    """Talk to someone - equivalent to V-TELL"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        character = self.get_object(parse_result.direct_object)
        
        if not character:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see them here."
            )
        
        if not character.has_flag(ObjectFlag.PERSON):
            return CommandResult(
                status=CommandStatus.FAILURE,
                message=f"You can't talk to the {character.name}."
            )
        
        # Get general response
        response = character.get_property('greeting')
        if not response:
            response = f"{character.name} acknowledges you."
        
        # Check character mood
        mood = self.world.character_manager.get_character_mood(character.id)
        if mood == 'suspicious':
            response = f"{character.name} eyes you suspiciously. \"{response}\""
        elif mood == 'hostile':
            response = f"{character.name} glares at you. \"I have nothing to say to you.\""
        else:
            response = f"{character.name} says, \"{response}\""
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=response
        )


class AskCommand(Command):
    """Ask someone about something - equivalent to V-ASK-ABOUT"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object and parse_result.text
    
    def execute(self, parse_result) -> CommandResult:
        character = self.get_object(parse_result.direct_object)
        topic = parse_result.text.lower()
        
        if not character:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see them here."
            )
        
        if not character.has_flag(ObjectFlag.PERSON):
            return CommandResult(
                status=CommandStatus.FAILURE,
                message=f"You can't ask the {character.name} about things."
            )
        
        # Get response for topic
        response = character.get_response(topic)
        
        # Format response
        formatted = f"{character.name} says, \"{response}\""
        
        # Check if this reveals evidence
        if topic in character.get_property('evidence_topics', []):
            evidence_id = f"{character.id}_{topic}_testimony"
            if not self.world.evidence_manager.has_evidence(evidence_id):
                self.world.evidence_manager.collect_evidence(evidence_id)
                formatted += "\n\n[You make a note of this testimony.]"
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=formatted
        )


class TellCommand(Command):
    """Tell someone about something - equivalent to V-TELL-ABOUT"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object and parse_result.text
    
    def execute(self, parse_result) -> CommandResult:
        character = self.get_object(parse_result.direct_object)
        topic = parse_result.text.lower()
        
        if not character:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see them here."
            )
        
        if not character.has_flag(ObjectFlag.PERSON):
            return CommandResult(
                status=CommandStatus.FAILURE,
                message=f"The {character.name} isn't listening."
            )
        
        # Check for specific reactions
        reactions = character.get_property('tell_reactions', {})
        if topic in reactions:
            response = reactions[topic]
        else:
            response = f"{character.name} nods but says nothing."
        
        # Update character state based on what was told
        if topic in ['murder', 'death', 'killing']:
            self.world.character_manager.make_suspicious(character.id)
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=response
        )


class ShowCommand(Command):
    """Show something to someone"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object and parse_result.indirect_object
    
    def execute(self, parse_result) -> CommandResult:
        obj = self.get_object(parse_result.direct_object)
        character = self.get_object(parse_result.indirect_object)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="You don't have that."
            )
        
        if not character:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see them here."
            )
        
        if not character.has_flag(ObjectFlag.PERSON):
            return CommandResult(
                status=CommandStatus.FAILURE,
                message=f"The {character.name} isn't interested."
            )
        
        # Check if object is in inventory
        if obj.location != self.player:
            return CommandResult(
                status=CommandStatus.FAILURE,
                message="You need to be carrying it first."
            )
        
        # Get character's reaction to the object
        reactions = character.get_property('show_reactions', {})
        if obj.id in reactions:
            response = reactions[obj.id]
        elif obj.get_property('evidence'):
            response = f"{character.name} examines the {obj.name} carefully."
            # Make character suspicious if shown evidence
            self.world.character_manager.make_suspicious(character.id)
        else:
            response = f"{character.name} glances at the {obj.name} but shows no interest."
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=response
        )


class AccuseCommand(Command):
    """Accuse someone of murder - game-winning command"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        character = self.get_object(parse_result.direct_object)
        
        if not character:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see them here."
            )
        
        if not character.has_flag(ObjectFlag.PERSON):
            return CommandResult(
                status=CommandStatus.FAILURE,
                message="You can only accuse people."
            )
        
        # Make the accusation
        success, message = self.world.evidence_manager.make_accusation(character.id)
        
        if success:
            # Game won!
            self.engine.state = GameState.WON
            self.engine.calculate_final_score()
        else:
            # Wrong accusation
            self.engine.state = GameState.LOST
        
        return CommandResult(
            status=CommandStatus.SUCCESS if success else CommandStatus.FAILURE,
            message=message,
            update_state=True
        )


class ArrestCommand(Command):
    """Arrest someone - alternative to accuse"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        # Arrest is functionally the same as accuse in this game
        return AccuseCommand(self.engine).execute(parse_result)