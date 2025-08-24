# 7_code_translation/src/deadline/core/game_engine.py
"""
Main game engine for Deadline Interactive Fiction
Translated from ZIL to Python 3.13
Preserves all original game logic while using modern Python patterns
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GameState(Enum):
    """Game state enumeration - matches ZIL game states"""
    PLAYING = auto()
    PAUSED = auto()
    ENDED = auto()
    WON = auto()
    LOST = auto()
    QUIT = auto()


@dataclass
class GameConfig:
    """Configuration for game engine - data-driven approach"""
    title: str = "Deadline"
    author: str = "Marc Blank"
    version: str = "1.0.0"
    max_score: int = 100
    max_moves: int = 1440  # 24 hours in minutes
    start_time: int = 480  # 8:00 AM in minutes since midnight
    time_limit: int = 720  # 12 hours game time
    debug_mode: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameConfig':
        """Create config from dictionary"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


class GameEngine:
    """
    Main game engine - translated from ZIL DEADLINE.ZIL
    Manages game state, coordinates subsystems, and drives gameplay
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize the game engine with data-driven configuration
        
        Args:
            data_path: Path to game data directory
        """
        self.data_path = data_path
        self.config = GameConfig()
        
        # Core game state - equivalent to ZIL globals
        self.state = GameState.PLAYING
        self.score = 0
        self.moves = 0
        self.current_time = self.config.start_time
        self.winner: Optional[str] = None
        
        # Game subsystems (will be initialized separately)
        self.world_manager = None
        self.parser = None
        self.time_manager = None
        self.command_processor = None
        self.interface = None
        self.save_manager = None
        
        # Game data storage
        self.game_data: Dict[str, Any] = {}
        self.vocabulary: Dict[str, Any] = {}
        self.syntax_rules: List[Dict] = []
        
        # Performance tracking
        self.performance_stats = {
            'commands_processed': 0,
            'total_processing_time': 0,
            'average_response_time': 0
        }
        
        logger.info(f"Game Engine initialized with data path: {data_path}")
    
    def load_game_data(self) -> bool:
        """
        Load all game data from JSON files
        Equivalent to ZIL's compile-time object definitions
        
        Returns:
            True if data loaded successfully
        """
        try:
            # Load main game data
            game_data_file = self.data_path / "game_data.json"
            if not game_data_file.exists():
                logger.error(f"Game data file not found: {game_data_file}")
                return False
                
            with open(game_data_file, 'r', encoding='utf-8') as f:
                self.game_data = json.load(f)
            
            # Load configuration from game data
            if 'config' in self.game_data:
                self.config = GameConfig.from_dict(self.game_data['config'])
            
            # Update start time from config
            self.current_time = self.config.start_time
            
            # Load vocabulary
            vocab_file = self.data_path / "vocabulary.json"
            if vocab_file.exists():
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    self.vocabulary = json.load(f)
            else:
                logger.warning(f"Vocabulary file not found: {vocab_file}")
                self.vocabulary = {"words": []}
            
            # Load syntax rules
            syntax_file = self.data_path / "syntax_rules.json"
            if syntax_file.exists():
                with open(syntax_file, 'r', encoding='utf-8') as f:
                    self.syntax_rules = json.load(f)
            else:
                logger.warning(f"Syntax rules file not found: {syntax_file}")
                self.syntax_rules = []
            
            logger.info(f"Game data loaded successfully: {self.config.title} v{self.config.version}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in game data: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load game data: {e}")
            return False
    
    def initialize_subsystems(self):
        """
        Initialize all game subsystems
        Equivalent to ZIL's initialization routines
        """
        from ..world.world_manager import WorldManager
        from ..parser.parser import GameParser
        from ..time.time_manager import TimeManager
        from ..commands.base_command import CommandProcessor
        from ..io.interface import GameInterface
        from ..io.save_system import SaveManager
        
        # Initialize world from data
        self.world_manager = WorldManager(self.game_data)
        self.world_manager.initialize_world()
        
        # Initialize parser with vocabulary
        self.parser = GameParser(self.vocabulary, self.syntax_rules)
        
        # Initialize time system
        self.time_manager = TimeManager(self.current_time)
        schedules_file = self.data_path / "schedules.json"
        if schedules_file.exists():
            self.time_manager.load_schedules(schedules_file)
        
        # Initialize command processor
        self.command_processor = CommandProcessor(self)
        
        # Initialize user interface
        self.interface = GameInterface(self)
        
        # Initialize save system
        self.save_manager = SaveManager(self)
        
        logger.info("All subsystems initialized")
    
    def start_game(self):
        """
        Start the game - main game loop
        Equivalent to ZIL's main routine
        """
        # Display intro
        self.interface.display_intro()
        
        # Display initial room
        current_room = self.world_manager.get_current_room()
        if current_room:
            self.interface.display_room(current_room)
        
        # Main game loop
        while self.state == GameState.PLAYING:
            try:
                # Get player input
                command = self.interface.get_input()
                
                if not command:
                    continue
                
                # Process command
                result = self.process_command(command)
                
                # Display result
                if result:
                    self.interface.display_result(result)
                
                # Update game state only if command consumed time
                if result and result.get('consumed_time', True):
                    self.update_game_state()
                
                # Check win/lose conditions
                self.check_game_conditions()
                
            except KeyboardInterrupt:
                self.quit_game()
                break
            except Exception as e:
                logger.error(f"Game error: {e}", exc_info=True)
                self.interface.display_error(str(e))
        
        # Game ended - display appropriate ending
        self.display_ending()
    
    def process_command(self, command_text: str) -> Dict[str, Any]:
        """
        Process a player command through the full pipeline
        Equivalent to ZIL's command processing routines
        
        Args:
            command_text: Raw input from player
            
        Returns:
            Result dictionary with status and message
        """
        import time
        start_time = time.perf_counter()
        
        try:
            # Parse the command
            parse_result = self.parser.parse(command_text)
            
            if not parse_result.is_valid:
                return {
                    'status': 'error',
                    'message': parse_result.error_message or "I don't understand that.",
                    'consumed_time': False
                }
            
            # Execute the command
            command_result = self.command_processor.execute(parse_result)
            
            # Update statistics
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            self.performance_stats['commands_processed'] += 1
            self.performance_stats['total_processing_time'] += processing_time
            self.performance_stats['average_response_time'] = (
                self.performance_stats['total_processing_time'] / 
                self.performance_stats['commands_processed']
            )
            
            # Log performance if in debug mode
            if self.config.debug_mode:
                logger.debug(f"Command '{command_text}' processed in {processing_time:.3f}s")
            
            return command_result
            
        except Exception as e:
            logger.error(f"Error processing command '{command_text}': {e}")
            return {
                'status': 'error',
                'message': "An error occurred processing that command.",
                'consumed_time': False
            }
    
    def update_game_state(self):
        """
        Update game state after each turn
        Equivalent to ZIL's per-turn updates
        """
        # Increment move counter
        self.moves += 1
        
        # Advance game time
        self.current_time += 1
        self.time_manager.advance_time(1)
        
        # Process scheduled events
        events = self.time_manager.get_current_events()
        for event in events:
            self.process_event(event)
        
        # Update NPCs
        self.world_manager.update_characters(self.current_time)
        
        # Update score based on evidence collected
        evidence_value = self.world_manager.evidence_manager.get_evidence_value()
        if evidence_value > self.score:
            self.score = evidence_value
    
    def check_game_conditions(self):
        """
        Check for win/lose conditions
        Equivalent to ZIL's victory and failure checking
        """
        # Check time limit
        if self.current_time >= self.config.start_time + self.config.time_limit:
            self.state = GameState.LOST
            self.winner = "time"
            return
        
        # Check victory conditions (murder solved)
        if self.check_murder_solved():
            self.state = GameState.WON
            self.calculate_final_score()
            return
        
        # Check failure conditions
        if self.check_failure_conditions():
            self.state = GameState.LOST
            return
    
    def check_murder_solved(self) -> bool:
        """
        Check if the player has successfully solved the murder
        Equivalent to ZIL's victory condition checking
        """
        # Check if player has accused the correct person with sufficient evidence
        evidence_manager = self.world_manager.evidence_manager
        
        if evidence_manager.accusation_made:
            correct_murderer = self.game_data.get('solution', {}).get('murderer')
            player_accusation = evidence_manager.accused_person
            
            if player_accusation == correct_murderer:
                # Check if player has sufficient evidence
                required_evidence = set(self.game_data.get('solution', {}).get('required_evidence', []))
                collected_evidence = set(evidence_manager.collected_evidence)
                
                if required_evidence.issubset(collected_evidence):
                    return True
                else:
                    # Right person, insufficient evidence
                    self.winner = "insufficient_evidence"
        
        return False
    
    def check_failure_conditions(self) -> bool:
        """
        Check for game failure conditions
        """
        # Check if player made wrong accusation
        evidence_manager = self.world_manager.evidence_manager
        
        if evidence_manager.accusation_made:
            correct_murderer = self.game_data.get('solution', {}).get('murderer')
            if evidence_manager.accused_person != correct_murderer:
                self.winner = "wrong_accusation"
                return True
        
        return False
    
    def calculate_final_score(self):
        """
        Calculate final game score
        Equivalent to ZIL's scoring system
        """
        base_score = 50  # For solving the murder
        
        # Bonus for speed
        time_taken = self.current_time - self.config.start_time
        if time_taken < 180:  # Less than 3 hours
            base_score += 30
        elif time_taken < 360:  # Less than 6 hours
            base_score += 20
        elif time_taken < 540:  # Less than 9 hours
            base_score += 10
        
        # Bonus for evidence collected
        evidence_manager = self.world_manager.evidence_manager
        evidence_count = len(evidence_manager.collected_evidence)
        base_score += min(evidence_count * 2, 20)
        
        # Bonus for minimal moves
        if self.moves < 100:
            base_score += 10
        elif self.moves < 200:
            base_score += 5
        
        self.score = min(base_score, self.config.max_score)
    
    def process_event(self, event):
        """
        Process a scheduled event
        Equivalent to ZIL's daemon/fuse processing
        """
        from ..time.events import EventType
        
        event_type = event.event_type
        
        if event_type == EventType.CHARACTER_MOVEMENT:
            character_id = event.get_character_id()
            destination = event.get_location()
            if character_id and destination:
                self.world_manager.move_character(character_id, destination)
            
        elif event_type == EventType.CHARACTER_ACTION:
            character_id = event.get_character_id()
            action = event.get_action()
            if character_id and action:
                self.world_manager.character_action(character_id, action)
            
        elif event_type == EventType.PHONE_CALL:
            message = event.get_message()
            if message and self.world_manager.get_current_room().id == event.get_location():
                self.interface.display_result({'status': 'info', 'message': message})
            
        elif event_type == EventType.GAME_OVER:
            self.state = GameState.LOST
            self.winner = "time"
    
    def display_ending(self):
        """
        Display appropriate game ending
        """
        if self.state == GameState.WON:
            self.interface.display_victory(self.score)
        elif self.state == GameState.LOST:
            if self.winner == "time":
                self.interface.display_timeout()
            elif self.winner == "wrong_accusation":
                self.interface.display_failure()
            elif self.winner == "insufficient_evidence":
                self.interface.display_result({
                    'status': 'failure',
                    'message': "You identified the right person but lack sufficient evidence for a conviction."
                })
            else:
                self.interface.display_failure()
        elif self.state == GameState.QUIT:
            self.interface.display_quit()
    
    def save_game(self, filename: str = None) -> bool:
        """
        Save the current game state
        Equivalent to ZIL's SAVE routine
        """
        try:
            return self.save_manager.save(filename)
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False
    
    def load_game(self, filename: str) -> bool:
        """
        Load a saved game state
        Equivalent to ZIL's RESTORE routine
        """
        try:
            return self.save_manager.load(filename)
        except Exception as e:
            logger.error(f"Load failed: {e}")
            return False
    
    def quit_game(self):
        """
        Quit the game gracefully
        """
        self.state = GameState.QUIT
        logger.info("Game quit by player")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information about current game state
        """
        current_room = self.world_manager.get_current_room() if self.world_manager else None
        return {
            'state': self.state.name,
            'score': self.score,
            'moves': self.moves,
            'time': f"{self.time_manager.get_time_string() if self.time_manager else 'N/A'}",
            'current_room': current_room.id if current_room else None,
            'evidence_collected': len(self.world_manager.evidence_manager.collected_evidence) if self.world_manager else 0,
            'performance': self.performance_stats
        }