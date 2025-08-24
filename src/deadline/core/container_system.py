# 7_code_translation/src/deadline/core/container_system.py
"""
Container and containment system - translated from ZIL containment
"""

from typing import List, Optional, Set, TYPE_CHECKING
from .flags import ObjectFlag
from typing import Dict

if TYPE_CHECKING:
    from .game_object import GameObject

class ContainerSystem:
    """
    Manages object containment relationships
    Equivalent to ZIL's IN/CONTAINS system
    """
    
    def __init__(self):
        self._contents: Dict[str, List[str]] = {}
        self._locations: Dict[str, Optional[str]] = {}
    
    def add_to_container(self, obj_id: str, container_id: str):
        """Add an object to a container"""
        # Remove from previous container
        if obj_id in self._locations:
            old_container = self._locations[obj_id]
            if old_container and old_container in self._contents:
                if obj_id in self._contents[old_container]:
                    self._contents[old_container].remove(obj_id)
        
        # Add to new container
        if container_id not in self._contents:
            self._contents[container_id] = []
        
        if obj_id not in self._contents[container_id]:
            self._contents[container_id].append(obj_id)
        
        self._locations[obj_id] = container_id
    
    def remove_from_container(self, obj_id: str):
        """Remove an object from its container"""
        if obj_id in self._locations:
            container_id = self._locations[obj_id]
            if container_id and container_id in self._contents:
                if obj_id in self._contents[container_id]:
                    self._contents[container_id].remove(obj_id)
            self._locations[obj_id] = None
    
    def get_contents(self, container_id: str) -> List[str]:
        """Get all objects in a container"""
        return self._contents.get(container_id, []).copy()
    
    def get_location(self, obj_id: str) -> Optional[str]:
        """Get the container of an object"""
        return self._locations.get(obj_id)
    
    def is_in(self, obj_id: str, container_id: str, recursive: bool = True) -> bool:
        """
        Check if an object is in a container
        Equivalent to ZIL's IN?
        """
        current_location = self._locations.get(obj_id)
        
        while current_location:
            if current_location == container_id:
                return True
            
            if not recursive:
                break
            
            # Check parent container
            current_location = self._locations.get(current_location)
        
        return False
    
    def get_all_contents(self, container_id: str, recursive: bool = True) -> List[str]:
        """
        Get all contents, optionally recursive
        Equivalent to ZIL's FIRST?/NEXT? iteration
        """
        result = []
        direct_contents = self._contents.get(container_id, [])
        result.extend(direct_contents)
        
        if recursive:
            for obj_id in direct_contents:
                result.extend(self.get_all_contents(obj_id, recursive=True))
        
        return result
    
    def find_containers_with(self, obj_id: str) -> List[str]:
        """Find all containers that contain a specific object"""
        containers = []
        for container_id, contents in self._contents.items():
            if obj_id in contents:
                containers.append(container_id)
        return containers
    
    def clear_container(self, container_id: str):
        """Remove all objects from a container"""
        if container_id in self._contents:
            for obj_id in self._contents[container_id].copy():
                self._locations[obj_id] = None
            self._contents[container_id].clear()
    
    def can_contain(self, container: 'GameObject', obj: 'GameObject') -> bool:
        """
        Check if a container can hold an object
        Considers capacity, size, and flags
        """
        # Check if it's a container or surface
        if not (container.has_flag(ObjectFlag.CONTAINER) or container.has_flag(ObjectFlag.SURFACE)):
            return False
        
        # Check if container is open (if applicable)
        if container.has_flag(ObjectFlag.CONTAINER) and not container.has_flag(ObjectFlag.OPEN):
            if container.has_flag(ObjectFlag.LOCKED):
                return False
        
        # Check capacity
        capacity = container.get_property('capacity', float('inf'))
        current_count = len(self.get_contents(container.id))
        if current_count >= capacity:
            return False
        
        # Check size constraints
        max_size = container.get_property('max_item_size')
        if max_size and obj.get_property('size', 1) > max_size:
            return False
        
        # Can't contain itself
        if container.id == obj.id:
            return False
        
        # Can't create circular containment
        if self.is_in(container.id, obj.id):
            return False
        
        return True