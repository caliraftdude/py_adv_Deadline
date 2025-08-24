# 7_code_translation/src/deadline/world/room_manager.py
"""
Room management system - handles room navigation and descriptions
"""
from typing import Any
from typing import Dict, List, Optional, Set
from ..core.game_object import Room
from ..core.flags import ObjectFlag

class RoomManager:
    """Manages all rooms and navigation"""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.connections: Dict[str, Dict[str, str]] = {}
        
    def initialize(self, rooms: Dict[str, Room]):
        """Initialize with room data"""
        self.rooms = rooms
        self._build_connections()
    
    def _build_connections(self):
        """Build connection map from room exits"""
        self.connections = {}
        for room_id, room in self.rooms.items():
            self.connections[room_id] = room.exits.copy()
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID"""
        return self.rooms.get(room_id)
    
    def get_exit_description(self, room: Room) -> str:
        """Get description of available exits"""
        exits = room.get_available_exits()
        if not exits:
            return "There are no obvious exits."
        
        if len(exits) == 1:
            return f"There is an exit to the {exits[0]}."
        
        exit_str = ", ".join(exits[:-1])
        return f"There are exits to the {exit_str} and {exits[-1]}."
    
    def find_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """Find shortest path between two rooms"""
        if start_id not in self.rooms or end_id not in self.rooms:
            return None
        
        if start_id == end_id:
            return [start_id]
        
        # BFS to find shortest path
        from collections import deque
        
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            for direction, next_id in self.connections.get(current_id, {}).items():
                if next_id == end_id:
                    return path + [next_id]
                
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))
        
        return None
    
    def get_rooms_with_property(self, property_name: str, value: Any = None) -> List[Room]:
        """Find all rooms with a specific property"""
        matching_rooms = []
        for room in self.rooms.values():
            if room.has_property(property_name):
                if value is None or room.get_property(property_name) == value:
                    matching_rooms.append(room)
        return matching_rooms