# 7_code_translation/src/deadline/main.py
"""
Main entry point for Deadline Interactive Fiction
"""

import sys
import argparse
from pathlib import Path
import logging
from typing import Optional

from deadline.core.game_engine import GameEngine


def setup_logging(debug: bool = False):
    """Configure logging for the application"""
    level = logging.DEBUG if debug else logging.INFO
    format_str = '%(levelname)s - %(message)s' if not debug else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=level, format=format_str)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Deadline - An Interactive Fiction Mystery')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--load', type=str, help='Load a saved game')
    parser.add_argument('--data-path', type=str, help='Path to game data directory')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    # Determine data path
    if args.data_path:
        data_path = Path(args.data_path)
    else:
        # Try to find data directory
        # First try relative to the module
        module_dir = Path(__file__).parent
        data_path = module_dir / "data"
        
        if not data_path.exists():
            # Try current directory
            data_path = Path.cwd() / "data"
        
        if not data_path.exists():
            # Try parent directory (development mode)
            data_path = Path.cwd().parent / "data"
    
    if not data_path.exists():
        print(f"Error: Game data directory not found.")
        print(f"Searched in: {data_path}")
        print("Use --data-path to specify the location of the game data directory.")
        sys.exit(1)
    
    try:
        # Initialize game
        engine = GameEngine(data_path)
        
        # Set debug mode
        if args.debug:
            engine.config.debug_mode = True
        
        # Load game data
        if not engine.load_game_data():
            print("Error: Failed to load game data.")
            print(f"Make sure the following files exist in {data_path}:")
            print("  - game_data.json")
            print("  - vocabulary.json")
            print("  - syntax_rules.json")
            print("  - schedules.json")
            sys.exit(1)
        
        # Initialize subsystems
        engine.initialize_subsystems()
        
        # Load saved game if specified
        if args.load:
            if not engine.load_game(args.load):
                print(f"Warning: Could not load save file '{args.load}'. Starting new game.")
        
        # Start the game
        engine.start_game()
        
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("\nIf this error persists, please report it with the above details.")
        sys.exit(1)


if __name__ == "__main__":
    main()