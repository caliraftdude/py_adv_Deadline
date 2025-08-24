# 7_code_translation/tests/test_commands.py
"""Tests for command execution"""

import pytest
from unittest.mock import Mock, MagicMock
from deadline.commands.manipulation import TakeCommand
from deadline.commands.base_command import CommandStatus


class TestCommands:
    @pytest.fixture
    def mock_engine(self):
        engine = Mock()
        engine.world_manager = Mock()
        engine.world_manager.player = Mock()
        return engine
    
    def test_take_command(self, mock_engine):
        cmd = TakeCommand(mock_engine)
        parse_result = Mock()
        parse_result.direct_object = "key"
        
        # Mock object
        mock_obj = Mock()
        mock_obj.can_take.return_value = True
        mock_obj.location = None
        cmd.get_object = Mock(return_value=mock_obj)
        mock_engine.world_manager.player.can_carry.return_value = True
        
        result = cmd.execute(parse_result)
        assert result.status == CommandStatus.SUCCESS