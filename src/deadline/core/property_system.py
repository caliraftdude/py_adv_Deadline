# 7_code_translation/src/deadline/core/property_system.py
"""
Property management system - translated from ZIL property system
"""

from typing import Dict, Any, Optional, List
import copy

class PropertyManager:
    """
    Manages object properties - equivalent to ZIL's GETP/PUTP system
    """
    
    def __init__(self):
        self._properties: Dict[str, Dict[str, Any]] = {}
        self._defaults: Dict[str, Any] = {
            'size': 1,
            'weight': 1,
            'capacity': 10,
            'value': 0,
            'damage': 0,
            'strength': 10,
            'trust_level': 0,
        }
    
    def register_object(self, obj_id: str, initial_properties: Dict[str, Any] = None):
        """Register an object with the property system"""
        self._properties[obj_id] = initial_properties or {}
    
    def get_property(self, obj_id: str, prop_name: str, default: Any = None) -> Any:
        """
        Get a property value for an object
        Equivalent to ZIL's GETP
        """
        if obj_id not in self._properties:
            return default
        
        if prop_name in self._properties[obj_id]:
            return self._properties[obj_id][prop_name]
        
        # Check defaults
        if prop_name in self._defaults:
            return self._defaults[prop_name]
        
        return default
    
    def set_property(self, obj_id: str, prop_name: str, value: Any):
        """
        Set a property value for an object
        Equivalent to ZIL's PUTP
        """
        if obj_id not in self._properties:
            self._properties[obj_id] = {}
        
        self._properties[obj_id][prop_name] = value
    
    def has_property(self, obj_id: str, prop_name: str) -> bool:
        """Check if an object has a specific property"""
        if obj_id not in self._properties:
            return False
        return prop_name in self._properties[obj_id]
    
    def remove_property(self, obj_id: str, prop_name: str):
        """Remove a property from an object"""
        if obj_id in self._properties and prop_name in self._properties[obj_id]:
            del self._properties[obj_id][prop_name]
    
    def get_all_properties(self, obj_id: str) -> Dict[str, Any]:
        """Get all properties for an object"""
        if obj_id not in self._properties:
            return {}
        return copy.deepcopy(self._properties[obj_id])
    
    def clear_object(self, obj_id: str):
        """Clear all properties for an object"""
        if obj_id in self._properties:
            self._properties[obj_id].clear()
    
    def copy_properties(self, from_id: str, to_id: str):
        """Copy all properties from one object to another"""
        if from_id in self._properties:
            self._properties[to_id] = copy.deepcopy(self._properties[from_id])