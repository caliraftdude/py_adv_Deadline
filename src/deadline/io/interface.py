# 7_code_translation/src/deadline/io/interface.py
"""
Game interface - handles input/output with the player
"""
from typing import TYPE_CHECKING
from ..core.flags import ObjectFlag
if TYPE_CHECKING:
    from ..core.game_object import Room
    
from typing import Optional, List, Dict, Any
import sys
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns

from ..core.game_object import Room, GameObject
from .output_formatter import OutputFormatter


class GameInterface:
    """
    Main interface for player interaction
    Handles input, output, and display formatting
    """
    
    def __init__(self, engine):
        """Initialize interface with game engine reference"""
        self.engine = engine
        self.console = Console()
        self.formatter = OutputFormatter()
        self.command_history = InMemoryHistory()
        
        # Display settings
        self.use_color = True
        self.width = 80
        
    def display_intro(self):
        """Display game introduction"""
        intro_text = self.engine.game_data.get('intro_text', 'Welcome to Deadline.')
        
        panel = Panel(
            intro_text,
            title="[bold red]DEADLINE[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def get_input(self, prompt_text: str = "> ") -> str:
        """
        Get input from player with enhanced features
        Includes command history and auto-suggestions
        """
        try:
            user_input = prompt(
                prompt_text,
                history=self.command_history,
                auto_suggest=AutoSuggestFromHistory(),
            )
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"
    
    def display_room(self, room: Room):
        """Display room description with objects and exits"""
        if not room:
            return
        
        # Room name
        self.console.print(f"[bold cyan]{room.name}[/bold cyan]")
        
        # Room description
        if room.has_flag(ObjectFlag.VISITED):
            description = room.visited_description or room.description
        else:
            description = room.description
        
        self.console.print(self.formatter.wrap_text(description))
        
        # List visible objects
        visible_objects = []
        for obj in room.contents:
            if obj.is_visible() and obj != self.engine.world_manager.player:
                visible_objects.append(obj)
        
        if visible_objects:
            self.console.print()
            for obj in visible_objects:
                if obj.has_flag(ObjectFlag.PERSON):
                    self.console.print(f"[yellow]{obj.name} is here.[/yellow]")
                else:
                    article = obj.get_article()
                    if article:
                        self.console.print(f"There is {article} [green]{obj.name}[/green] here.")
                    else:
                        self.console.print(f"[green]{obj.name}[/green] is here.")
        
        # Show exits
        self.console.print()
        exit_text = self.engine.world_manager.room_manager.get_exit_description(room)
        self.console.print(f"[dim]{exit_text}[/dim]")
        
        # Show time
        self.console.print()
        self.display_status_line()
    
    def display_result(self, result: Dict[str, Any]):
        """Display command execution result"""
        message = result.get('message', '')
        status = result.get('status', 'success')
        
        if message:
            if status == 'error':
                self.console.print(f"[red]{message}[/red]")
            elif status == 'warning':
                self.console.print(f"[yellow]{message}[/yellow]")
            else:
                self.console.print(self.formatter.wrap_text(message))
    
    def display_error(self, error_msg: str):
        """Display an error message"""
        self.console.print(f"[bold red]Error: {error_msg}[/bold red]")
    
    def display_status_line(self):
        """Display status line with time, location, and score"""
        time_str = self.engine.time_manager.get_time_string()
        score_str = f"Score: {self.engine.score}"
        moves_str = f"Moves: {self.engine.moves}"
        
        status = f"[{time_str}] | {score_str} | {moves_str}"
        self.console.print(f"[dim]{status}[/dim]")
    
    def display_inventory(self):
        """Display player inventory"""
        inventory = self.engine.world_manager.player.get_inventory()
        
        if not inventory:
            self.console.print("You are carrying nothing.")
        else:
            self.console.print("You are carrying:")
            for item in inventory:
                self.console.print(f"  - {item.get_inventory_description()}")
    
    def display_victory(self, score: int):
        """Display victory message"""
        victory_text = self.engine.game_data.get('victory_text', 'You have won!')
        
        panel = Panel(
            f"{victory_text}\n\nFinal Score: {score}",
            title="[bold green]CASE SOLVED![/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def display_failure(self):
        """Display failure message"""
        failure_text = self.engine.game_data.get('failure_text', 'You have failed.')
        
        panel = Panel(
            failure_text,
            title="[bold red]CASE UNSOLVED[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def display_timeout(self):
        """Display timeout message"""
        timeout_text = self.engine.game_data.get('timeout_text', 'Time has run out.')
        
        panel = Panel(
            timeout_text,
            title="[bold yellow]TIME'S UP[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def display_quit(self):
        """Display quit message"""
        self.console.print("\n[italic]Thanks for playing Deadline![/italic]")
    
    def confirm(self, message: str) -> bool:
        """Get yes/no confirmation from player"""
        while True:
            response = self.get_input(f"{message} (yes/no) > ")
            response = response.lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                self.console.print("Please answer yes or no.")