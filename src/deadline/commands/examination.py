# 7_code_translation/src/deadline/commands/examination.py
"""
Examination commands - looking at and searching objects
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..parser.parser import ParseResult

from .base_command import Command, CommandResult, CommandStatus
from ..core.flags import ObjectFlag


class LookCommand(Command):
    """Look around - equivalent to V-LOOK"""
    
    def can_execute(self, parse_result) -> bool:
        return True
    
    def execute(self, parse_result) -> CommandResult:
        current_room = self.world.get_current_room()
        
        if not current_room:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="You're not in a valid location."
            )
        
        # Redisplay room description
        from ..io.interface import GameInterface
        interface = GameInterface(self.engine)
        interface.display_room(current_room)
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message="",
            consumed_time=False  # Looking doesn't consume time
        )


class ExamineCommand(Command):
    """Examine an object - equivalent to V-EXAMINE"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        obj_ref = parse_result.direct_object
        
        # Special case for "me" or "self"
        if obj_ref.lower() in ['me', 'myself', 'self']:
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message="You're a professional detective, here to investigate the death of Marshall Robner.",
                consumed_time=False
            )
        
        obj = self.get_object(obj_ref)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see that here."
            )
        
        # Get detailed description
        description = obj.get_description(detailed=True)
        
        # Check for hidden objects
        if obj.has_flag(ObjectFlag.CONTAINER):
            if obj.has_flag(ObjectFlag.OPEN):
                if obj.contents:
                    items = ", ".join([item.name for item in obj.contents if item.is_visible()])
                    description += f"\n\nThe {obj.name} contains: {items}"
                else:
                    description += f"\n\nThe {obj.name} is empty."
            elif obj.has_flag(ObjectFlag.TRANSPARENT):
                if obj.contents:
                    items = ", ".join([item.name for item in obj.contents if item.is_visible()])
                    description += f"\n\nThrough the {obj.name} you can see: {items}"
        
        # Mark as evidence if examining reveals it
        if obj.get_property('evidence') and obj.has_flag(ObjectFlag.HIDDEN):
            obj.clear_flag(ObjectFlag.HIDDEN)
            self.world.evidence_manager.collect_evidence(obj.id)
            description += "\n\n[This looks like important evidence!]"
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=description,
            consumed_time=False
        )


class SearchCommand(Command):
    """Search an object thoroughly - equivalent to V-SEARCH"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        obj = self.get_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see that here."
            )
        
        # Check if already searched
        if obj.has_flag(ObjectFlag.SEARCHED):
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"You've already thoroughly searched the {obj.name}."
            )
        
        # Mark as searched
        obj.set_flag(ObjectFlag.SEARCHED)
        
        # Check for hidden items
        found_items = []
        for item in obj.contents:
            if item.has_flag(ObjectFlag.HIDDEN):
                item.clear_flag(ObjectFlag.HIDDEN)
                found_items.append(item)
                
                # Collect evidence if applicable
                if item.get_property('evidence'):
                    self.world.evidence_manager.collect_evidence(item.id)
        
        if found_items:
            items_text = ", ".join([f"a {item.name}" for item in found_items])
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"Searching the {obj.name}, you find: {items_text}"
            )
        else:
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message=f"You search the {obj.name} thoroughly but find nothing of interest."
            )


class ReadCommand(Command):
    """Read something - equivalent to V-READ"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        obj = self.get_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see that here."
            )
        
        if not obj.has_flag(ObjectFlag.READABLE):
            return CommandResult(
                status=CommandStatus.FAILURE,
                message=f"There's nothing to read on the {obj.name}."
            )
        
        # Get readable text
        text = obj.get_property('readable_text')
        if not text:
            text = obj.description
        
        # Mark as evidence if applicable
        if obj.get_property('evidence') and not self.world.evidence_manager.has_evidence(obj.id):
            self.world.evidence_manager.collect_evidence(obj.id)
            text += "\n\n[This seems important to the case!]"
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=text,
            consumed_time=False
        )


class LookUnderCommand(Command):
    """Look under something"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        obj = self.get_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see that here."
            )
        
        # Check for items hidden under
        under_items = obj.get_property('under_items', [])
        if under_items:
            # Reveal hidden items
            found = []
            for item_id in under_items:
                if item_id in self.world.objects:
                    item = self.world.objects[item_id]
                    if item.has_flag(ObjectFlag.HIDDEN):
                        item.clear_flag(ObjectFlag.HIDDEN)
                        item.move_to(obj.location)
                        found.append(item)
            
            if found:
                items_text = ", ".join([f"a {item.name}" for item in found])
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=f"Looking under the {obj.name}, you find: {items_text}"
                )
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=f"There's nothing under the {obj.name}.",
            consumed_time=False
        )


class LookBehindCommand(Command):
    """Look behind something"""
    
    def can_execute(self, parse_result) -> bool:
        return parse_result.direct_object is not None
    
    def execute(self, parse_result) -> CommandResult:
        obj = self.get_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult(
                status=CommandStatus.ERROR,
                message="I don't see that here."
            )
        
        # Check for items hidden behind
        behind_items = obj.get_property('behind_items', [])
        if behind_items:
            # Reveal hidden items
            found = []
            for item_id in behind_items:
                if item_id in self.world.objects:
                    item = self.world.objects[item_id]
                    if item.has_flag(ObjectFlag.HIDDEN):
                        item.clear_flag(ObjectFlag.HIDDEN)
                        item.move_to(obj.location)
                        found.append(item)
            
            if found:
                items_text = ", ".join([f"a {item.name}" for item in found])
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=f"Looking behind the {obj.name}, you find: {items_text}"
                )
        
        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=f"There's nothing behind the {obj.name}.",
            consumed_time=False
        )