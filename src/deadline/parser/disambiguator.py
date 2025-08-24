# 7_code_translation/src/deadline/parser/disambiguator.py
"""
Disambiguation system for resolving ambiguous object references
"""

from typing import List, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..core.game_object import GameObject
    from ..world.world_manager import WorldManager

logger = logging.getLogger(__name__)


class Disambiguator:
    """
    Resolves ambiguous object references
    Equivalent to ZIL's disambiguation routines
    """
    
    def __init__(self, world_manager: 'WorldManager'):
        """Initialize with world manager reference"""
        self.world = world_manager
        self.last_disambiguation: Optional[List['GameObject']] = None
    
    def disambiguate(self, word: str, adjectives: List[str] = None,
                     context: str = None) -> Optional['GameObject']:
        """
        Disambiguate an object reference
        
        Args:
            word: The noun to disambiguate
            adjectives: Any adjectives modifying the noun
            context: Context hint (e.g., 'take', 'examine')
            
        Returns:
            The disambiguated object, or None if cannot resolve
        """
        # Find all matching objects
        candidates = self._find_candidates(word, adjectives)
        
        if not candidates:
            return None
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Apply disambiguation strategies
        
        # 1. Prefer visible objects
        visible = [obj for obj in candidates if obj.is_visible()]
        if len(visible) == 1:
            return visible[0]
        elif visible:
            candidates = visible
        
        # 2. Prefer accessible objects
        accessible = [obj for obj in candidates if obj.is_accessible()]
        if len(accessible) == 1:
            return accessible[0]
        elif accessible:
            candidates = accessible
        
        # 3. Consider context
        if context:
            contextual = self._apply_context(candidates, context)
            if len(contextual) == 1:
                return contextual[0]
            elif contextual:
                candidates = contextual
        
        # 4. Prefer objects in current room over inventory
        current_room = self.world.get_current_room()
        if current_room:
            in_room = [obj for obj in candidates if obj.location == current_room]
            if len(in_room) == 1:
                return in_room[0]
            elif in_room:
                candidates = in_room
        
        # 5. If still ambiguous, store for potential clarification
        if len(candidates) > 1:
            self.last_disambiguation = candidates
            return None
        
        return candidates[0] if candidates else None
    
    def _find_candidates(self, word: str, adjectives: List[str] = None) -> List['GameObject']:
        """Find all objects matching the word and adjectives"""
        candidates = []
        
        # Search in current room and inventory
        visible_objects = self.world.get_visible_objects()
        
        for obj in visible_objects:
            # Check name match
            if obj.name.lower() == word.lower():
                if self._check_adjectives(obj, adjectives):
                    candidates.append(obj)
                    continue
            
            # Check synonyms
            for synonym in obj.synonyms:
                if synonym.lower() == word.lower():
                    if self._check_adjectives(obj, adjectives):
                        candidates.append(obj)
                        break
        
        return candidates
    
    def _check_adjectives(self, obj: 'GameObject', adjectives: List[str] = None) -> bool:
        """Check if object matches the given adjectives"""
        if not adjectives:
            return True
        
        obj_adjectives = [adj.lower() for adj in obj.adjectives]
        for adj in adjectives:
            if adj.lower() not in obj_adjectives:
                return False
        return True
    
    def _apply_context(self, candidates: List['GameObject'], context: str) -> List['GameObject']:
        """Apply context-specific filtering"""
        filtered = []
        
        if context == 'take':
            # Prefer takeable objects
            filtered = [obj for obj in candidates if obj.can_take()]
        elif context == 'open' or context == 'close':
            # Prefer containers
            from ..core.flags import ObjectFlag
            filtered = [obj for obj in candidates if obj.has_flag(ObjectFlag.CONTAINER)]
        elif context == 'read':
            # Prefer readable objects
            from ..core.flags import ObjectFlag
            filtered = [obj for obj in candidates if obj.has_flag(ObjectFlag.READABLE)]
        elif context == 'talk':
            # Prefer people
            from ..core.flags import ObjectFlag
            filtered = [obj for obj in candidates if obj.has_flag(ObjectFlag.PERSON)]
        
        return filtered if filtered else candidates
    
    def get_last_ambiguous(self) -> Optional[List['GameObject']]:
        """Get the last set of ambiguous objects"""
        return self.last_disambiguation
    
    def clear_ambiguity(self):
        """Clear stored ambiguity"""
        self.last_disambiguation = None