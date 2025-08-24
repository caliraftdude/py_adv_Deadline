# 7_code_translation/src/deadline/io/save_system.py
"""
Save/load system for game state persistence
"""
from typing import List
from ..core.game_engine import GameState

import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..core.exceptions import SaveLoadException

logger = logging.getLogger(__name__)


class SaveManager:
    """
    Manages game save and load operations
    Equivalent to ZIL's SAVE/RESTORE commands
    """
    
    def __init__(self, engine):
        """Initialize save manager with engine reference"""
        self.engine = engine
        self.save_dir = Path.home() / ".deadline_saves"
        self.save_dir.mkdir(exist_ok=True)
        
    def save(self, filename: str = None) -> bool:
        """
        Save current game state
        
        Args:
            filename: Save file name (optional, auto-generated if not provided)
            
        Returns:
            True if save successful
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"deadline_save_{timestamp}.sav"
            
            save_path = self.save_dir / filename
            
            # Gather game state
            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'engine_state': self._get_engine_state(),
                'world_state': self._get_world_state(),
                'time_state': self._get_time_state(),
                'evidence_state': self._get_evidence_state()
            }
            
            # Save to file
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            logger.info(f"Game saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Save failed: {e}")
            raise SaveLoadException(f"Failed to save game: {e}")
    
    def load(self, filename: str) -> bool:
        """
        Load a saved game state
        
        Args:
            filename: Save file to load
            
        Returns:
            True if load successful
        """
        try:
            save_path = self.save_dir / filename
            
            if not save_path.exists():
                # Try without directory
                save_path = Path(filename)
                if not save_path.exists():
                    raise SaveLoadException(f"Save file not found: {filename}")
            
            # Load save data
            with open(save_path, 'rb') as f:
                save_data = pickle.load(f)
            
            # Validate version
            if save_data.get('version') != '1.0':
                raise SaveLoadException("Incompatible save file version")
            
            # Restore state
            self._restore_engine_state(save_data['engine_state'])
            self._restore_world_state(save_data['world_state'])
            self._restore_time_state(save_data['time_state'])
            self._restore_evidence_state(save_data['evidence_state'])
            
            logger.info(f"Game loaded from {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Load failed: {e}")
            raise SaveLoadException(f"Failed to load game: {e}")
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """List available save files"""
        saves = []
        
        for save_file in self.save_dir.glob("*.sav"):
            try:
                with open(save_file, 'rb') as f:
                    save_data = pickle.load(f)
                
                saves.append({
                    'filename': save_file.name,
                    'timestamp': save_data.get('timestamp'),
                    'score': save_data.get('engine_state', {}).get('score', 0),
                    'moves': save_data.get('engine_state', {}).get('moves', 0)
                })
            except:
                continue
        
        return sorted(saves, key=lambda x: x['timestamp'], reverse=True)
    
    def delete_save(self, filename: str) -> bool:
        """Delete a save file"""
        try:
            save_path = self.save_dir / filename
            if save_path.exists():
                save_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete save: {e}")
            return False
    
    def _get_engine_state(self) -> Dict[str, Any]:
        """Get engine state for saving"""
        return {
            'state': self.engine.state.name,
            'score': self.engine.score,
            'moves': self.engine.moves,
            'current_time': self.engine.current_time,
            'winner': self.engine.winner
        }
    
    def _get_world_state(self) -> Dict[str, Any]:
        """Get world state for saving"""
        world = self.engine.world_manager
        
        # Save object states
        object_states = {}
        for obj_id, obj in world.objects.items():
            object_states[obj_id] = obj.save_state()
        
        return {
            'current_room_id': world.current_room_id,
            'object_states': object_states,
            'character_states': world.character_manager.character_states
        }
    
    def _get_time_state(self) -> Dict[str, Any]:
        """Get time state for saving"""
        time_mgr = self.engine.time_manager
        return {
            'current_time': time_mgr.current_time,
            'current_day': time_mgr.current_day,
            'time_stopped': time_mgr.time_stopped
        }
    
    def _get_evidence_state(self) -> Dict[str, Any]:
        """Get evidence state for saving"""
        evidence = self.engine.world_manager.evidence_manager
        return {
            'collected_evidence': list(evidence.collected_evidence),
            'accusation_made': evidence.accusation_made,
            'accused_person': evidence.accused_person,
            'case_solved': evidence.case_solved
        }
    
    def _restore_engine_state(self, state: Dict[str, Any]):
        """Restore engine state from save"""
        from ..core.game_engine import GameState
        
        self.engine.state = GameState[state['state']]
        self.engine.score = state['score']
        self.engine.moves = state['moves']
        self.engine.current_time = state['current_time']
        self.engine.winner = state['winner']
    
    def _restore_world_state(self, state: Dict[str, Any]):
        """Restore world state from save"""
        world = self.engine.world_manager
        
        # Restore object states
        for obj_id, obj_state in state['object_states'].items():
            if obj_id in world.objects:
                world.objects[obj_id].load_state(obj_state)
        
        # Restore object locations
        for obj_id, obj_state in state['object_states'].items():
            if obj_id in world.objects and 'location' in obj_state:
                location_id = obj_state['location']
                if location_id and location_id in world.objects:
                    world.objects[obj_id].move_to(world.objects[location_id])
        
        world.current_room_id = state['current_room_id']
        world.character_manager.character_states = state['character_states']
    
    def _restore_time_state(self, state: Dict[str, Any]):
        """Restore time state from save"""
        time_mgr = self.engine.time_manager
        time_mgr.current_time = state['current_time']
        time_mgr.current_day = state['current_day']
        time_mgr.time_stopped = state['time_stopped']
    
    def _restore_evidence_state(self, state: Dict[str, Any]):
        """Restore evidence state from save"""
        evidence = self.engine.world_manager.evidence_manager
        evidence.collected_evidence = set(state['collected_evidence'])
        evidence.accusation_made = state['accusation_made']
        evidence.accused_person = state['accused_person']
        evidence.case_solved = state['case_solved']