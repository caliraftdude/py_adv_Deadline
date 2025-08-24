# 7_code_translation/src/deadline/parser/syntax.py
"""
Syntax rules and patterns for command parsing
"""
import json
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum


class SlotType(Enum):
    """Types of slots in syntax patterns"""
    VERB = "verb"
    DIRECT_OBJECT = "direct_object"
    INDIRECT_OBJECT = "indirect_object"
    PREPOSITION = "preposition"
    DIRECTION = "direction"
    TEXT = "text"


@dataclass
class SyntaxRule:
    """A syntax rule for command parsing"""
    pattern: str
    verb: str
    slots: List[SlotType]
    prepositions: List[str] = None
    regex: re.Pattern = None
    
    def __post_init__(self):
        if self.prepositions is None:
            self.prepositions = []
        
        # Compile regex pattern
        if not self.regex:
            self.regex = self._compile_pattern()
    
    def _compile_pattern(self) -> re.Pattern:
        """Compile pattern string to regex"""
        # Convert pattern placeholders to regex groups
        pattern = self.pattern.lower()
        pattern = pattern.replace('object', r'(.+?)')
        pattern = pattern.replace('direction', r'(north|south|east|west|up|down|in|out)')
        pattern = pattern.replace('text', r'(.+)')
        
        # Handle prepositions
        if self.prepositions:
            prep_pattern = '|'.join(self.prepositions)
            pattern = pattern.replace('preposition', f'({prep_pattern})')
        
        return re.compile(f'^{pattern}$', re.IGNORECASE)
    
    def match(self, text: str) -> Optional[Tuple[bool, Dict[str, str]]]:
        """
        Try to match text against this rule
        Returns (success, slot_values)
        """
        match = self.regex.match(text.lower())
        if not match:
            return None
        
        # Extract slot values
        slot_values = {'verb': self.verb}
        groups = match.groups()
        
        for i, slot in enumerate(self.slots):
            if i < len(groups):
                slot_values[slot.value] = groups[i]
        
        return True, slot_values


class SyntaxRules:
    """
    Collection of syntax rules for the game
    Equivalent to ZIL's SYNTAX definitions
    """
    
    def __init__(self):
        self.rules: List[SyntaxRule] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize with default syntax rules"""
        # Movement
        self.add_rule("go direction", "go", [SlotType.DIRECTION])
        self.add_rule("direction", "go", [SlotType.DIRECTION])
        
        # Object manipulation
        self.add_rule("take object", "take", [SlotType.DIRECT_OBJECT])
        self.add_rule("get object", "take", [SlotType.DIRECT_OBJECT])
        self.add_rule("drop object", "drop", [SlotType.DIRECT_OBJECT])
        self.add_rule("put object in object", "put", [SlotType.DIRECT_OBJECT, SlotType.INDIRECT_OBJECT], ["in", "into"])
        self.add_rule("put object on object", "put", [SlotType.DIRECT_OBJECT, SlotType.INDIRECT_OBJECT], ["on", "onto"])

        # Examination
        self.add_rule("look", "look", [])
        self.add_rule("look at object", "examine", [SlotType.DIRECT_OBJECT])
        self.add_rule("examine object", "examine", [SlotType.DIRECT_OBJECT])
        self.add_rule("search object", "search", [SlotType.DIRECT_OBJECT])
        self.add_rule("read object", "read", [SlotType.DIRECT_OBJECT])
        
        # Container operations
        self.add_rule("open object", "open", [SlotType.DIRECT_OBJECT])
        self.add_rule("close object", "close", [SlotType.DIRECT_OBJECT])
        self.add_rule("lock object", "lock", [SlotType.DIRECT_OBJECT])
        self.add_rule("unlock object", "unlock", [SlotType.DIRECT_OBJECT])
        self.add_rule("lock object with object", "lock", [SlotType.DIRECT_OBJECT, SlotType.INDIRECT_OBJECT], ["with"])
        self.add_rule("unlock object with object", "unlock", [SlotType.DIRECT_OBJECT, SlotType.INDIRECT_OBJECT], ["with"])

        # Communication
        self.add_rule("talk to object", "talk", [SlotType.DIRECT_OBJECT], ["to"])
        self.add_rule("ask object about text", "ask", [SlotType.DIRECT_OBJECT, SlotType.TEXT], ["about"])
        self.add_rule("tell object about text", "tell", [SlotType.DIRECT_OBJECT, SlotType.TEXT], ["about"])

        # Meta commands
        self.add_rule("save", "save", [])
        self.add_rule("restore", "restore", [])
        self.add_rule("quit", "quit", [])
        self.add_rule("inventory", "inventory", [])
        self.add_rule("score", "score", [])
        self.add_rule("wait", "wait", [])
    
    def add_rule(self, pattern: str, verb: str, slots: List[SlotType], prepositions: List[str] = None):
        """Add a syntax rule"""
        rule = SyntaxRule(pattern, verb, slots, prepositions)
        self.rules.append(rule)
    
    def load_from_file(self, filepath: Path):
        """Load syntax rules from JSON file"""
        try:
            with open(filepath, 'r') as f:
                rules_data = json.load(f)
            
            for rule_data in rules_data:
                slots = [SlotType[s.upper()] for s in rule_data.get('slots', [])]
                self.add_rule(
                    pattern=rule_data['pattern'],
                    verb=rule_data['verb'],
                    slots=slots,
                    prepositions=rule_data.get('prepositions')
                )
            
            logger.info(f"Loaded {len(rules_data)} syntax rules")
            
        except Exception as e:
            logger.error(f"Failed to load syntax rules: {e}")
    
    def match_input(self, text: str) -> Optional[Dict[str, str]]:
        """
        Try to match input text against all rules
        Returns slot values if match found
        """
        for rule in self.rules:
            result = rule.match(text)
            if result:
                return result[1]  # Return slot values
        
        return None