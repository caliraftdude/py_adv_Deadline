# 7_code_translation/tests/test_game.py
"""Integration tests for the complete game"""

import pytest
from pathlib import Path
from deadline.core.game_engine import GameEngine, GameState
import json

class TestGameIntegration:
    @pytest.fixture
    def game_engine(self, tmp_path):
        # Create minimal test data
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create test data files
        game_data = {
            "config": {"title": "Test", "max_score": 100},
            "player": {"starting_room": "test_room"},
            "rooms": {
                "test_room": {
                    "name": "Test Room",
                    "description": "A test room."
                }
            }
        }
        
        (data_dir / "game_data.json").write_text(json.dumps(game_data))
        (data_dir / "vocabulary.json").write_text('{"words": []}')
        (data_dir / "syntax_rules.json").write_text('[]')
        (data_dir / "schedules.json").write_text('{"events": []}')
        
        engine = GameEngine(data_dir)
        engine.load_game_data()
        return engine
    
    def test_game_initialization(self, game_engine):
        assert game_engine.state == GameState.PLAYING
        assert game_engine.score == 0
