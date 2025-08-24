# 7_code_translation/src/deadline/io/output_formatter.py
"""
Output formatting utilities
"""

import textwrap
from typing import List, Optional
import re


class OutputFormatter:
    """
    Formats text output for display
    Handles word wrapping, formatting codes, etc.
    """
    
    def __init__(self, width: int = 80):
        """Initialize formatter with display width"""
        self.width = width
        self.indent = "  "
    
    def wrap_text(self, text: str, width: Optional[int] = None) -> str:
        """
        Wrap text to specified width
        Preserves paragraph breaks
        """
        if not text:
            return ""
        
        width = width or self.width
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        wrapped_paragraphs = []
        
        for paragraph in paragraphs:
            # Wrap each paragraph
            wrapped = textwrap.fill(
                paragraph,
                width=width,
                break_long_words=False,
                break_on_hyphens=False
            )
            wrapped_paragraphs.append(wrapped)
        
        return '\n\n'.join(wrapped_paragraphs)
    
    def format_list(self, items: List[str], bullet: str = "•") -> str:
        """Format a list of items with bullets"""
        if not items:
            return ""
        
        formatted = []
        for item in items:
            wrapped = textwrap.fill(
                f"{bullet} {item}",
                width=self.width,
                subsequent_indent=self.indent
            )
            formatted.append(wrapped)
        
        return '\n'.join(formatted)
    
    def format_dialogue(self, speaker: str, text: str) -> str:
        """Format character dialogue"""
        return f'"{text}"\n    -- {speaker}'
    
    def format_evidence(self, evidence_list: List[str]) -> str:
        """Format evidence list"""
        if not evidence_list:
            return "No evidence collected."
        
        header = "Evidence Collected:"
        items = self.format_list(evidence_list, "•")
        
        return f"{header}\n{items}"
    
    def format_score(self, score: int, max_score: int, moves: int) -> str:
        """Format score display"""
        percentage = (score / max_score * 100) if max_score > 0 else 0
        return f"Score: {score}/{max_score} ({percentage:.0f}%) in {moves} moves"
    
    def format_time(self, time_str: str, location: str = None) -> str:
        """Format time and location display"""
        if location:
            return f"[{time_str}] - {location}"
        return f"[{time_str}]"
    
    def remove_formatting(self, text: str) -> str:
        """Remove any formatting codes from text"""
        # Remove rich formatting codes
        text = re.sub(r'\[.*?\]', '', text)
        return text
    
    def highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """Highlight specific keywords in text"""
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            text = pattern.sub(f"[bold]{keyword}[/bold]", text)
        return text