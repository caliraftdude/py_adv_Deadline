# 7_code_translation/tests/test_world.py
"""Tests for world management"""

import pytest
from deadline.core.game_object import GameObject, Room, ObjectFlag
from deadline.world.world_manager import WorldManager


class TestWorldManager:
    def test_object_creation(self):
        obj = GameObject(
            id="test_obj",
            name="Test Object",
            flags=ObjectFlag.TAKEABLE
        )
        assert obj.has_flag(ObjectFlag.TAKEABLE)
        assert obj.can_take()
    
    def test_room_exits(self):
        room = Room(
            id="test_room",
            name="Test Room",
            exits={"north": "other_room"}
        )
        assert room.get_exit("north") == "other_room"
        assert room.get_exit("south") is None