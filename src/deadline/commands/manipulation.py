# 7_code_translation/src/deadline/commands/manipulation.py
"""
Object manipulation commands
Translated from ZIL verb implementations
"""

from typing import Optional, List
from .base_command import Command, CommandResult, CommandStatus, ManipulationCommand
from ..core.game_object import GameObject, ObjectFlag, Container, Character
import logging

logger = logging.getLogger(__name__)


class TakeCommand(ManipulationCommand):
    """Take/get an object - equivalent to V-TAKE"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Take what?")
        
        # Try to find the object
        obj = self.get_room_object(parse_result.direct_object)
        
        if not obj:
            # Check if already carried
            if self.get_held_object(parse_result.direct_object):
                return CommandResult.failure("You're already carrying that.")
            return CommandResult.error("I don't see that here.")
        
        # Check if object is accessible
        if not obj.is_accessible():
            container = obj.location
            if container and container.has_flag(ObjectFlag.CONTAINER):
                if not container.has_flag(ObjectFlag.OPEN):
                    return CommandResult.failure(
                        f"You need to open the {container.name} first."
                    )
            return CommandResult.failure("You can't reach that.")
        
        # Check if takeable
        if not obj.can_take():
            if obj.has_flag(ObjectFlag.SACRED):
                return CommandResult.failure("That's too important to take.")
            elif obj.has_flag(ObjectFlag.PERSON):
                return CommandResult.failure("You can't pick up people!")
            else:
                return CommandResult.failure("You can't take that.")
        
        # Check if player can carry it
        if not self.player.can_carry(obj):
            carried = len(self.player.get_inventory())
            if carried >= self.player.max_carry_items:
                return CommandResult.failure(
                    "You're carrying too many things. Try dropping something first."
                )
            else:
                return CommandResult.failure("That's too heavy to carry.")
        
        # Take the object
        obj.move_to(self.player)
        
        # Mark as evidence if applicable
        if obj.get_property('evidence') and self.world:
            if hasattr(self.world, 'evidence_manager'):
                self.world.evidence_manager.collect_evidence(obj.id)
                
                # Check if this is critical evidence
                if obj.get_property('evidence_value', 0) > 10:
                    return CommandResult.success(
                        f"Taken.\n(This looks like important evidence!)",
                        data={'evidence_collected': obj.id}
                    )
        
        # Special message for certain items
        if obj.has_flag(ObjectFlag.LIGHT):
            if obj.has_flag(ObjectFlag.ON):
                return CommandResult.success(
                    f"You take the {obj.name} (providing light)."
                )
        
        return CommandResult.success("Taken.")


class DropCommand(ManipulationCommand):
    """Drop an object - equivalent to V-DROP"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Drop what?")
        
        obj = self.get_held_object(parse_result.direct_object)
        
        if not obj:
            # Check if it's in the room
            if self.get_room_object(parse_result.direct_object):
                return CommandResult.failure("You're not carrying that.")
            return CommandResult.error("I don't see that here.")
        
        # Check if droppable
        if obj.has_flag(ObjectFlag.SACRED):
            return CommandResult.failure("You can't drop that here.")
        
        # Check if worn
        if obj.has_flag(ObjectFlag.WEARABLE) and obj.get_property('worn'):
            return CommandResult.failure("You need to take it off first.")
        
        # Drop the object
        current_room = self.get_current_room()
        if not current_room:
            return CommandResult.error("You're nowhere!")
        
        obj.move_to(current_room)
        
        # Special messages
        if obj.has_flag(ObjectFlag.LIGHT) and obj.has_flag(ObjectFlag.ON):
            return CommandResult.success(
                f"You drop the {obj.name} (still providing light)."
            )
        
        return CommandResult.success("Dropped.")


class OpenCommand(ManipulationCommand):
    """Open something - equivalent to V-OPEN"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Open what?")
        
        obj = self.get_visible_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult.error("I don't see that here.")
        
        # Check if it can be opened
        if not obj.has_flag(ObjectFlag.CONTAINER):
            if hasattr(obj, '__class__') and obj.__class__.__name__ == 'Door':
                # Special handling for doors
                if obj.has_flag(ObjectFlag.LOCKED):
                    return CommandResult.failure("It's locked.")
                if obj.has_flag(ObjectFlag.OPEN):
                    return CommandResult.failure("It's already open.")
                obj.set_flag(ObjectFlag.OPEN)
                return CommandResult.success(f"You open the {obj.name}.")
            return CommandResult.failure("You can't open that.")
        
        if obj.has_flag(ObjectFlag.OPEN):
            return CommandResult.failure("It's already open.")
        
        if obj.has_flag(ObjectFlag.LOCKED):
            key_id = obj.get_property('key_id')
            if key_id:
                # Check if player has the key
                key = self.get_held_object(key_id)
                if key:
                    return CommandResult.failure(
                        f"It's locked. Try unlocking it with the {key.name}."
                    )
            return CommandResult.failure("It's locked.")
        
        # Open it
        obj.set_flag(ObjectFlag.OPEN)
        
        # Describe contents if any
        if obj.contents:
            visible_contents = [item for item in obj.contents if item.is_visible()]
            if visible_contents:
                items = ", ".join([item.get_inventory_description() 
                                 for item in visible_contents])
                message = f"You open the {obj.name}, revealing: {items}."
            else:
                message = f"You open the {obj.name}."
        else:
            message = f"You open the {obj.name}. It's empty."
        
        return CommandResult.success(message)


class CloseCommand(ManipulationCommand):
    """Close something - equivalent to V-CLOSE"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Close what?")
        
        obj = self.get_visible_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult.error("I don't see that here.")
        
        # Check if it can be closed
        if not obj.has_flag(ObjectFlag.CONTAINER):
            if hasattr(obj, '__class__') and obj.__class__.__name__ == 'Door':
                # Special handling for doors
                if not obj.has_flag(ObjectFlag.OPEN):
                    return CommandResult.failure("It's already closed.")
                obj.clear_flag(ObjectFlag.OPEN)
                return CommandResult.success(f"You close the {obj.name}.")
            return CommandResult.failure("You can't close that.")
        
        if not obj.has_flag(ObjectFlag.OPEN):
            return CommandResult.failure("It's already closed.")
        
        # Close it
        obj.clear_flag(ObjectFlag.OPEN)
        
        return CommandResult.success(f"You close the {obj.name}.")


class LockCommand(ManipulationCommand):
    """Lock something - equivalent to V-LOCK"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Lock what?")
        
        obj = self.get_visible_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult.error("I don't see that here.")
        
        # Check if it can be locked
        key_id = obj.get_property('key_id')
        if not key_id:
            return CommandResult.failure("That doesn't have a lock.")
        
        # Check if player has the key
        key = None
        if parse_result.indirect_object:
            # Key specified in command
            key = self.get_held_object(parse_result.indirect_object)
            if not key:
                return CommandResult.failure(
                    f"You don't have the {parse_result.indirect_object}."
                )
            if key.id != key_id:
                return CommandResult.failure(f"The {key.name} doesn't fit.")
        else:
            # Look for the right key
            key = self.get_held_object(key_id)
            if not key:
                # Try to find key by name
                for item in self.player.contents:
                    if item.id == key_id:
                        key = item
                        break
                
                if not key:
                    return CommandResult.failure(
                        f"You need the right key to lock the {obj.name}."
                    )
        
        if obj.has_flag(ObjectFlag.LOCKED):
            return CommandResult.failure("It's already locked.")
        
        if obj.has_flag(ObjectFlag.OPEN):
            return CommandResult.failure("You need to close it first.")
        
        # Lock it
        obj.set_flag(ObjectFlag.LOCKED)
        
        return CommandResult.success(f"You lock the {obj.name} with the {key.name}.")


class UnlockCommand(ManipulationCommand):
    """Unlock something - equivalent to V-UNLOCK"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Unlock what?")
        
        obj = self.get_visible_object(parse_result.direct_object)
        
        if not obj:
            return CommandResult.error("I don't see that here.")
        
        if not obj.has_flag(ObjectFlag.LOCKED):
            if obj.has_flag(ObjectFlag.CONTAINER) or \
               (hasattr(obj, '__class__') and obj.__class__.__name__ == 'Door'):
                return CommandResult.failure("It's not locked.")
            return CommandResult.failure("That doesn't have a lock.")
        
        # Check for key
        key_id = obj.get_property('key_id')
        if not key_id:
            # Shouldn't happen if object is locked, but check anyway
            obj.clear_flag(ObjectFlag.LOCKED)
            return CommandResult.success(f"You unlock the {obj.name}.")
        
        # Find the key
        key = None
        if parse_result.indirect_object:
            # Key specified in command
            key = self.get_held_object(parse_result.indirect_object)
            if not key:
                return CommandResult.failure(
                    f"You don't have the {parse_result.indirect_object}."
                )
            if key.id != key_id:
                return CommandResult.failure(f"The {key.name} doesn't fit.")
        else:
            # Look for the right key
            key = self.get_held_object(key_id)
            if not key:
                # Try to find key by checking all inventory items
                for item in self.player.contents:
                    if item.id == key_id:
                        key = item
                        break
                
                if not key:
                    return CommandResult.failure(
                        f"You need the right key to unlock the {obj.name}."
                    )
        
        # Unlock it
        obj.clear_flag(ObjectFlag.LOCKED)
        
        # Auto-open containers after unlocking (common IF convention)
        if obj.has_flag(ObjectFlag.CONTAINER) and not obj.has_flag(ObjectFlag.OPEN):
            obj.set_flag(ObjectFlag.OPEN)
            
            # Check contents
            if obj.contents:
                visible_contents = [item for item in obj.contents if item.is_visible()]
                if visible_contents:
                    items = ", ".join([item.get_inventory_description() 
                                     for item in visible_contents])
                    return CommandResult.success(
                        f"You unlock and open the {obj.name} with the {key.name}, "
                        f"revealing: {items}."
                    )
            
            return CommandResult.success(
                f"You unlock and open the {obj.name} with the {key.name}."
            )
        
        return CommandResult.success(f"You unlock the {obj.name} with the {key.name}.")


class PutCommand(ManipulationCommand):
    """Put object in/on something - equivalent to V-PUT"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Put what?")
        
        if not parse_result.indirect_object:
            return CommandResult.failure(f"Put the {parse_result.direct_object} where?")
        
        # Get the object to put
        obj = self.get_held_object(parse_result.direct_object)
        if not obj:
            obj = self.get_room_object(parse_result.direct_object)
            if not obj:
                return CommandResult.error("I don't see that here.")
            if obj.location != self.player:
                return CommandResult.failure("You need to take it first.")
        
        # Get the container
        container = self.get_visible_object(parse_result.indirect_object)
        if not container:
            return CommandResult.error(
                f"I don't see the {parse_result.indirect_object} here."
            )
        
        # Can't put something in itself
        if obj == container:
            return CommandResult.failure("You can't put something inside itself!")
        
        # Check if container can hold objects
        if not container.has_flag(ObjectFlag.CONTAINER) and \
           not container.has_flag(ObjectFlag.SURFACE):
            return CommandResult.failure(
                f"You can't put things in the {container.name}."
            )
        
        # Check if container is open
        if container.has_flag(ObjectFlag.CONTAINER):
            if not container.has_flag(ObjectFlag.OPEN):
                return CommandResult.failure(
                    f"The {container.name} is closed."
                )
        
        # Check capacity
        if not container.can_contain(obj):
            capacity = container.get_property('capacity')
            if capacity and len(container.contents) >= capacity:
                return CommandResult.failure(
                    f"The {container.name} is full."
                )
            else:
                return CommandResult.failure(
                    f"The {obj.name} won't fit in the {container.name}."
                )
        
        # Move object to container
        obj.move_to(container)
        
        # Determine preposition
        if container.has_flag(ObjectFlag.SURFACE):
            prep = "on"
        else:
            prep = "in"
        
        return CommandResult.success(
            f"You put the {obj.name} {prep} the {container.name}."
        )


class GiveCommand(ManipulationCommand):
    """Give object to someone - equivalent to V-GIVE"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Give what?")
        
        if not parse_result.indirect_object:
            return CommandResult.failure(f"Give the {parse_result.direct_object} to whom?")
        
        # Get the object to give
        obj = self.get_held_object(parse_result.direct_object)
        if not obj:
            if self.get_room_object(parse_result.direct_object):
                return CommandResult.failure("You need to take it first.")
            return CommandResult.error("You don't have that.")
        
        # Get the recipient
        recipient = self.get_room_object(parse_result.indirect_object)
        if not recipient:
            return CommandResult.error("I don't see them here.")
        
        # Check if recipient is a person
        if not recipient.has_flag(ObjectFlag.PERSON):
            return CommandResult.failure(
                f"You can only give things to people, not to the {recipient.name}."
            )
        
        # Check if character will accept the item
        if isinstance(recipient, Character):
            # Check character's reaction to the gift
            reaction = recipient.react_to_action('give', obj)
            
            # Check if character refuses the item
            if recipient.get_property('refuses_items'):
                refused = recipient.get_property('refuses_items')
                if obj.id in refused or 'all' in refused:
                    return CommandResult.failure(
                        reaction or f"{recipient.name} doesn't want the {obj.name}."
                    )
            
            # Special handling for evidence
            if obj.get_property('evidence'):
                # Character might reveal information when given evidence
                trust_change = obj.get_property('evidence_value', 0) // 5
                recipient.trust_level = recipient.trust_level + trust_change
                
                # Move object to character
                obj.move_to(recipient)
                
                if reaction:
                    return CommandResult.success(reaction)
                else:
                    return CommandResult.success(
                        f"{recipient.name} takes the {obj.name} and examines it carefully."
                    )
            
            # Give object to character
            obj.move_to(recipient)
            
            if reaction:
                return CommandResult.success(reaction)
            else:
                return CommandResult.success(
                    f"{recipient.name} accepts the {obj.name}."
                )
        
        # Fallback for non-Character persons
        obj.move_to(recipient)
        return CommandResult.success(f"You give the {obj.name} to {recipient.name}.")


class WearCommand(ManipulationCommand):
    """Wear/put on clothing - equivalent to V-WEAR"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Wear what?")
        
        obj = self.get_held_object(parse_result.direct_object)
        if not obj:
            obj = self.get_room_object(parse_result.direct_object)
            if obj:
                return CommandResult.failure("You need to take it first.")
            return CommandResult.error("I don't see that here.")
        
        if not obj.has_flag(ObjectFlag.WEARABLE):
            return CommandResult.failure("You can't wear that.")
        
        if obj.get_property('worn'):
            return CommandResult.failure("You're already wearing it.")
        
        # Check for conflicting worn items
        worn_type = obj.get_property('wear_type', 'clothing')
        for item in self.player.contents:
            if item != obj and item.has_flag(ObjectFlag.WEARABLE):
                if item.get_property('worn') and \
                   item.get_property('wear_type', 'clothing') == worn_type:
                    return CommandResult.failure(
                        f"You're already wearing the {item.name}."
                    )
        
        obj.set_property('worn', True)
        return CommandResult.success(f"You put on the {obj.name}.")


class RemoveCommand(ManipulationCommand):
    """Remove/take off clothing - equivalent to V-REMOVE"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Remove what?")
        
        obj = self.get_held_object(parse_result.direct_object)
        if not obj:
            return CommandResult.error("You're not wearing that.")
        
        if not obj.has_flag(ObjectFlag.WEARABLE):
            return CommandResult.failure("You're not wearing that.")
        
        if not obj.get_property('worn'):
            return CommandResult.failure("You're not wearing it.")
        
        obj.set_property('worn', False)
        return CommandResult.success(f"You take off the {obj.name}.")


class ThrowCommand(ManipulationCommand):
    """Throw an object - equivalent to V-THROW"""
    
    def can_execute(self, parse_result):
        return parse_result.direct_object is not None
    
    def execute(self, parse_result):
        if not parse_result.direct_object:
            return CommandResult.failure("Throw what?")
        
        obj = self.get_held_object(parse_result.direct_object)
        if not obj:
            return CommandResult.error("You're not carrying that.")
        
        # If target specified
        if parse_result.indirect_object:
            target = self.get_visible_object(parse_result.indirect_object)
            if not target:
                return CommandResult.error(
                    f"I don't see the {parse_result.indirect_object} here."
                )
            
            # Check if throwing at a person
            if target.has_flag(ObjectFlag.PERSON):
                # Drop the object
                room = self.get_current_room()
                obj.move_to(room)
                
                # Get reaction
                if isinstance(target, Character):
                    reaction = target.react_to_action('throw', obj)
                    if reaction:
                        return CommandResult.success(reaction)
                
                return CommandResult.success(
                    f"You throw the {obj.name} at {target.name}. "
                    f"It bounces off and falls to the floor."
                )
            else:
                # Throwing at an object
                room = self.get_current_room()
                obj.move_to(room)
                
                # Check if target breaks
                if target.get_property('fragile'):
                    return CommandResult.success(
                        f"You throw the {obj.name} at the {target.name}. "
                        f"The {target.name} shatters!"
                    )
                
                return CommandResult.success(
                    f"You throw the {obj.name} at the {target.name}. "
                    f"The {obj.name} falls to the floor."
                )
        
        # No target - just drop it forcefully
        room = self.get_current_room()
        obj.move_to(room)
        
        # Check if object breaks
        if obj.get_property('fragile'):
            obj.set_property('broken', True)
            return CommandResult.success(
                f"You throw the {obj.name} to the ground. It shatters!"
            )
        
        return CommandResult.success(
            f"You throw the {obj.name} to the ground."
        )