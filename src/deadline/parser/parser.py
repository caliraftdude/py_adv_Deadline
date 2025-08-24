# 7_code_translation/src/deadline/parser/parser.py
"""
Natural language parser for game commands
Translated from ZIL PARSER.ZIL
Handles player input and converts to game commands
"""

import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)


class WordType(Enum):
    """Word types in vocabulary - matches ZIL word types"""
    VERB = auto()
    NOUN = auto()
    ADJECTIVE = auto()
    PREPOSITION = auto()
    ARTICLE = auto()
    CONJUNCTION = auto()
    DIRECTION = auto()
    NUMBER = auto()
    SPECIAL = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Parsed token from input"""
    text: str
    word_type: Optional[WordType] = None
    canonical_form: Optional[str] = None
    object_ids: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"Token('{self.text}', {self.word_type.name if self.word_type else 'None'})"


@dataclass
class ParseResult:
    """Result of parsing a command"""
    is_valid: bool
    verb: Optional[str] = None
    direct_object: Optional[str] = None
    indirect_object: Optional[str] = None
    preposition: Optional[str] = None
    tokens: List[Token] = field(default_factory=list)
    error_message: Optional[str] = None
    ambiguous_objects: List[str] = field(default_factory=list)
    raw_input: str = ""
    
    def __repr__(self):
        if self.is_valid:
            return f"ParseResult(verb='{self.verb}', dobj='{self.direct_object}', iobj='{self.indirect_object}')"
        return f"ParseResult(invalid: {self.error_message})"


@dataclass
class VocabularyEntry:
    """Entry in the vocabulary database"""
    word: str
    word_type: WordType
    canonical: Optional[str] = None
    objects: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyntaxPattern:
    """Syntax pattern for command matching"""
    pattern: str
    verb: str
    slots: List[str]
    prepositions: List[str] = field(default_factory=list)
    regex: Optional[re.Pattern] = None
    
    def __post_init__(self):
        """Compile pattern to regex"""
        if not self.regex:
            self.regex = self._compile_pattern()
    
    def _compile_pattern(self) -> re.Pattern:
        """Convert syntax pattern to regex"""
        # Convert pattern like "VERB OBJECT PREP OBJECT" to regex
        pattern_str = self.pattern.lower()
        
        # Replace placeholders with capture groups
        pattern_str = re.sub(r'\bverb\b', r'(\w+)', pattern_str)
        pattern_str = re.sub(r'\bobject\d?\b', r'(.+?)', pattern_str)
        pattern_str = re.sub(r'\bprep\b', r'(\w+)', pattern_str)
        pattern_str = re.sub(r'\bdirection\b', r'(\w+)', pattern_str)
        
        return re.compile(f'^{pattern_str}$', re.IGNORECASE)


class GameParser:
    """
    Main parser class - translates natural language to game commands
    Equivalent to ZIL's PARSER routine and supporting functions
    """
    
    def __init__(self, vocabulary: Dict[str, Any] = None, syntax_rules: List[Dict] = None):
        """
        Initialize parser with vocabulary and syntax rules
        
        Args:
            vocabulary: Dictionary of words and their properties
            syntax_rules: List of syntax patterns for commands
        """
        self.vocabulary_entries: Dict[str, List[VocabularyEntry]] = {}
        self.syntax_patterns: List[SyntaxPattern] = []
        
        # Load vocabulary if provided
        if vocabulary:
            self._load_vocabulary(vocabulary)
        
        # Load syntax rules if provided
        if syntax_rules:
            self._load_syntax_rules(syntax_rules)
        
        # Initialize standard word sets
        self._init_standard_words()
        
        # Command history for "again" functionality
        self.last_command = None
        self.last_parse_result = None
        
        # Context for disambiguation
        self.current_context = None
    
    def _init_standard_words(self):
        """Initialize standard parser words"""
        # Common articles (ignored in parsing)
        self.articles = {'a', 'an', 'the', 'some'}
        
        # Standard prepositions
        self.prepositions = {
            'in', 'on', 'at', 'to', 'with', 'from', 'into', 
            'onto', 'under', 'behind', 'about', 'for', 'through',
            'across', 'over', 'around', 'near', 'beside', 'between'
        }
        
        # Direction mappings
        self.directions = {
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
            'ne': 'northeast', 'nw': 'northwest', 
            'se': 'southeast', 'sw': 'southwest',
            'u': 'up', 'd': 'down', 
            'in': 'enter', 'out': 'exit'
        }
        
        # Full direction names
        self.direction_words = {
            'north', 'south', 'east', 'west',
            'northeast', 'northwest', 'southeast', 'southwest',
            'up', 'down', 'enter', 'exit', 'in', 'out'
        }
        
        # Command shortcuts
        self.shortcuts = {
            'i': 'inventory',
            'l': 'look',
            'x': 'examine',
            'z': 'wait',
            'g': 'again',
            'q': 'quit',
            'n': 'north',
            's': 'south',
            'e': 'east',
            'w': 'west'
        }
        
        # Conjunctions for multiple commands
        self.conjunctions = {'and', 'then', ',', '.'}
        
        # Special meta-commands
        self.meta_commands = {
            'save', 'restore', 'load', 'quit', 'restart',
            'score', 'inventory', 'help', 'about', 'verbose',
            'brief', 'superbrief', 'version', 'transcript'
        }
    
    def _load_vocabulary(self, vocabulary: Dict[str, Any]):
        """Load vocabulary from configuration"""
        for word_data in vocabulary.get('words', []):
            word = word_data['word'].lower()
            
            entry = VocabularyEntry(
                word=word,
                word_type=WordType[word_data['type'].upper()],
                canonical=word_data.get('canonical', word),
                objects=word_data.get('objects', []),
                properties=word_data.get('properties', {})
            )
            
            if word not in self.vocabulary_entries:
                self.vocabulary_entries[word] = []
            self.vocabulary_entries[word].append(entry)
    
    def _load_syntax_rules(self, syntax_rules: List[Dict]):
        """Load syntax patterns from configuration"""
        for rule in syntax_rules:
            pattern = SyntaxPattern(
                pattern=rule['pattern'],
                verb=rule['verb'],
                slots=rule.get('slots', []),
                prepositions=rule.get('prepositions', [])
            )
            self.syntax_patterns.append(pattern)
        
        # Add default patterns if none provided
        if not self.syntax_patterns:
            self._add_default_patterns()
    
    def _add_default_patterns(self):
        """Add default syntax patterns"""
        default_patterns = [
            # Single verb
            {'pattern': 'VERB', 'verb': '*', 'slots': []},
            
            # Verb + object
            {'pattern': 'VERB OBJECT', 'verb': '*', 'slots': ['direct_object']},
            
            # Verb + object + preposition + object
            {'pattern': 'VERB OBJECT PREP OBJECT', 'verb': '*', 
             'slots': ['direct_object', 'preposition', 'indirect_object']},
            
            # Movement
            {'pattern': 'go DIRECTION', 'verb': 'go', 'slots': ['direction']},
            {'pattern': 'DIRECTION', 'verb': 'go', 'slots': ['direction']},
            
            # Common patterns
            {'pattern': 'look at OBJECT', 'verb': 'examine', 'slots': ['direct_object']},
            {'pattern': 'look in OBJECT', 'verb': 'search', 'slots': ['direct_object']},
            {'pattern': 'talk to OBJECT', 'verb': 'talk', 'slots': ['direct_object']},
            {'pattern': 'ask OBJECT about OBJECT', 'verb': 'ask', 
             'slots': ['direct_object', 'topic']},
            {'pattern': 'tell OBJECT about OBJECT', 'verb': 'tell',
             'slots': ['direct_object', 'topic']},
            {'pattern': 'give OBJECT to OBJECT', 'verb': 'give',
             'slots': ['direct_object', 'indirect_object']},
            {'pattern': 'put OBJECT in OBJECT', 'verb': 'put',
             'slots': ['direct_object', 'indirect_object']},
            {'pattern': 'accuse OBJECT of OBJECT', 'verb': 'accuse',
             'slots': ['direct_object', 'crime']}
        ]
        
        for pattern_data in default_patterns:
            self.syntax_patterns.append(SyntaxPattern(
                pattern=pattern_data['pattern'],
                verb=pattern_data['verb'],
                slots=pattern_data.get('slots', [])
            ))
    
    def parse(self, input_text: str, context: Any = None) -> ParseResult:
        """
        Parse player input into a game command
        Equivalent to ZIL's main PARSER routine
        
        Args:
            input_text: Raw text from player
            context: Current game context for disambiguation
            
        Returns:
            ParseResult with parsed command or error
        """
        # Store context for disambiguation
        self.current_context = context
        
        # Handle empty input
        if not input_text or not input_text.strip():
            return ParseResult(
                is_valid=False,
                error_message="Please enter a command.",
                raw_input=input_text
            )
        
        # Clean and normalize input
        input_text = input_text.strip()
        original_input = input_text
        input_lower = input_text.lower()
        
        # Handle 'again' command
        if input_lower in ('g', 'again'):
            if self.last_parse_result and self.last_parse_result.is_valid:
                return self.last_parse_result
            return ParseResult(
                is_valid=False,
                error_message="No previous command to repeat.",
                raw_input=original_input
            )
        
        # Expand shortcuts
        first_word = input_lower.split()[0] if input_lower.split() else ""
        if first_word in self.shortcuts:
            input_text = input_text.replace(first_word, self.shortcuts[first_word], 1)
            input_lower = input_text.lower()
        
        # Check for multiple commands (split by conjunctions)
        commands = self._split_commands(input_text)
        
        # For now, handle only the first command
        # (Multi-command support could be added later)
        if commands:
            input_text = commands[0]
        
        # Tokenize input
        tokens = self._tokenize(input_text)
        
        if not tokens:
            return ParseResult(
                is_valid=False,
                error_message="I don't understand that.",
                raw_input=original_input
            )
        
        # Identify word types
        self._identify_word_types(tokens)
        
        # Try to match against syntax patterns
        result = self._match_patterns(tokens, input_text)
        
        # If no pattern matched, try basic parsing
        if not result.is_valid:
            result = self._basic_parse(tokens)
        
        # Set raw input
        result.raw_input = original_input
        
        # Store successful parse for 'again'
        if result.is_valid:
            self.last_command = original_input
            self.last_parse_result = result
        
        return result
    
    def _split_commands(self, input_text: str) -> List[str]:
        """Split input into multiple commands if conjunctions present"""
        # For now, just return single command
        # Could be enhanced to handle "take key and go north"
        return [input_text]
    
    def _tokenize(self, input_text: str) -> List[Token]:
        """
        Break input into tokens
        Handles punctuation and special characters
        """
        # Remove common punctuation but preserve it for splitting
        text = input_text.replace(',', ' , ')
        text = text.replace('.', ' . ')
        text = text.replace('!', '')
        text = text.replace('?', '')
        text = text.replace('"', '')
        text = text.replace("'", '')
        
        # Split on whitespace
        words = text.split()
        
        # Create tokens, filtering articles
        tokens = []
        skip_next = False
        
        for i, word in enumerate(words):
            if skip_next:
                skip_next = False
                continue
            
            word_lower = word.lower()
            
            # Skip articles unless they're part of an object name
            if word_lower in self.articles:
                # Check if next word might be a noun
                if i + 1 < len(words):
                    next_word = words[i + 1].lower()
                    if next_word not in self.prepositions:
                        continue  # Skip the article
            
            # Skip punctuation used as separators
            if word in ',.':
                continue
            
            tokens.append(Token(text=word_lower))
        
        return tokens
    
    def _identify_word_types(self, tokens: List[Token]):
        """
        Identify the type of each token using vocabulary
        Equivalent to ZIL's vocabulary lookup
        """
        for token in tokens:
            word = token.text
            
            # Check vocabulary
            if word in self.vocabulary_entries:
                entries = self.vocabulary_entries[word]
                if entries:
                    # Use first entry for now (could be improved with context)
                    entry = entries[0]
                    token.word_type = entry.word_type
                    token.canonical_form = entry.canonical
                    token.object_ids = entry.objects.copy()
                    continue
            
            # Check if it's a direction
            if word in self.directions:
                token.word_type = WordType.DIRECTION
                token.canonical_form = self.directions[word]
            elif word in self.direction_words:
                token.word_type = WordType.DIRECTION
                token.canonical_form = word
            
            # Check if it's a preposition
            elif word in self.prepositions:
                token.word_type = WordType.PREPOSITION
                token.canonical_form = word
            
            # Check if it's a number
            elif word.isdigit():
                token.word_type = WordType.NUMBER
                token.canonical_form = word
            
            # Check if it's a meta-command
            elif word in self.meta_commands:
                token.word_type = WordType.VERB
                token.canonical_form = word
            
            # Unknown word
            else:
                token.word_type = WordType.UNKNOWN
    
    def _match_patterns(self, tokens: List[Token], input_text: str) -> ParseResult:
        """
        Match tokens against syntax patterns
        Equivalent to ZIL's syntax matching
        """
        # Build a simplified string for pattern matching
        token_string = ' '.join([t.text for t in tokens])
        
        # Try each syntax pattern
        for pattern in self.syntax_patterns:
            # Special handling for direction-only commands
            if len(tokens) == 1 and tokens[0].word_type == WordType.DIRECTION:
                return ParseResult(
                    is_valid=True,
                    verb='go',
                    direct_object=tokens[0].canonical_form or tokens[0].text,
                    tokens=tokens
                )
            
            # Try to match pattern
            match = self._try_pattern_match(tokens, pattern)
            if match:
                return match
        
        # No pattern matched
        return ParseResult(
            is_valid=False,
            tokens=tokens,
            error_message="I don't understand that command."
        )
    
    def _try_pattern_match(self, tokens: List[Token], pattern: SyntaxPattern) -> Optional[ParseResult]:
        """Try to match tokens against a specific pattern"""
        # This is a simplified pattern matcher
        # In a full implementation, this would be more sophisticated
        
        # For now, check basic verb + object patterns
        if not tokens:
            return None
        
        # Check if first token is a verb
        if tokens[0].word_type != WordType.VERB and pattern.verb != '*':
            return None
        
        verb_token = tokens[0]
        verb = verb_token.canonical_form or verb_token.text
        
        # Single verb command
        if len(tokens) == 1 and len(pattern.slots) == 0:
            return ParseResult(
                is_valid=True,
                verb=verb,
                tokens=tokens
            )
        
        # Verb + object
        if len(tokens) >= 2 and 'direct_object' in pattern.slots:
            # Find the direct object tokens
            obj_tokens = []
            prep_index = -1
            
            for i in range(1, len(tokens)):
                if tokens[i].word_type == WordType.PREPOSITION:
                    prep_index = i
                    break
                obj_tokens.append(tokens[i])
            
            if obj_tokens:
                direct_obj = self._resolve_object(obj_tokens)
                
                # Check for indirect object
                indirect_obj = None
                preposition = None
                
                if prep_index > 0 and prep_index < len(tokens) - 1:
                    preposition = tokens[prep_index].text
                    iobj_tokens = tokens[prep_index + 1:]
                    indirect_obj = self._resolve_object(iobj_tokens)
                
                return ParseResult(
                    is_valid=True,
                    verb=verb,
                    direct_object=direct_obj,
                    indirect_object=indirect_obj,
                    preposition=preposition,
                    tokens=tokens
                )
        
        return None
    
    def _basic_parse(self, tokens: List[Token]) -> ParseResult:
        """
        Basic parsing when no pattern matches
        Try to extract at least verb and object
        """
        if not tokens:
            return ParseResult(
                is_valid=False,
                tokens=tokens,
                error_message="I don't understand that."
            )
        
        # Look for a verb
        verb_token = None
        verb_index = -1
        
        for i, token in enumerate(tokens):
            if token.word_type == WordType.VERB:
                verb_token = token
                verb_index = i
                break
        
        # If no verb found, check if first word could be a verb
        if not verb_token and tokens:
            # Assume first word is verb
            verb_token = tokens[0]
            verb_index = 0
        
        if not verb_token:
            return ParseResult(
                is_valid=False,
                tokens=tokens,
                error_message="I don't understand that command."
            )
        
        verb = verb_token.canonical_form or verb_token.text
        
        # Look for objects after the verb
        direct_obj = None
        indirect_obj = None
        preposition = None
        
        if verb_index < len(tokens) - 1:
            # Find direct object
            obj_tokens = []
            prep_index = -1
            
            for i in range(verb_index + 1, len(tokens)):
                if tokens[i].word_type == WordType.PREPOSITION:
                    prep_index = i
                    preposition = tokens[i].text
                    break
                obj_tokens.append(tokens[i])
            
            if obj_tokens:
                direct_obj = self._resolve_object(obj_tokens)
            
            # Find indirect object
            if prep_index > 0 and prep_index < len(tokens) - 1:
                iobj_tokens = tokens[prep_index + 1:]
                indirect_obj = self._resolve_object(iobj_tokens)
        
        # Return result even if we're not sure it's valid
        return ParseResult(
            is_valid=True,  # Optimistically assume it's valid
            verb=verb,
            direct_object=direct_obj,
            indirect_object=indirect_obj,
            preposition=preposition,
            tokens=tokens
        )
    
    def _resolve_object(self, tokens: List[Token]) -> Optional[str]:
        """
        Resolve object tokens to an object identifier
        Handles adjectives and disambiguation
        """
        if not tokens:
            return None
        
        # Build object description from tokens
        obj_words = []
        adjectives = []
        noun = None
        
        for token in tokens:
            if token.word_type == WordType.ADJECTIVE:
                adjectives.append(token.text)
            elif token.word_type == WordType.NOUN:
                noun = token.text
                # If token has associated object IDs, use first one
                if token.object_ids:
                    # TODO: Handle disambiguation if multiple objects
                    return token.object_ids[0]
            else:
                obj_words.append(token.text)
        
        # If we found a noun, return it
        if noun:
            return noun
        
        # Otherwise return all words joined
        if obj_words:
            return ' '.join(obj_words)
        elif adjectives:
            return ' '.join(adjectives)
        
        # Last resort - return first token
        return tokens[0].text if tokens else None
    
    def disambiguate(self, objects: List[str], context: Any) -> Optional[str]:
        """
        Disambiguate between multiple matching objects
        Equivalent to ZIL's disambiguation routines
        
        Args:
            objects: List of possible object IDs
            context: Game context for disambiguation
            
        Returns:
            Selected object ID or None
        """
        if not objects:
            return None
        
        # If only one object, return it
        if len(objects) == 1:
            return objects[0]
        
        # TODO: Implement smart disambiguation based on context
        # For now, return the first object
        return objects[0]
    
    def add_vocabulary(self, word: str, word_type: WordType, 
                       canonical: str = None, objects: List[str] = None):
        """Add a word to the vocabulary dynamically"""
        entry = VocabularyEntry(
            word=word.lower(),
            word_type=word_type,
            canonical=canonical or word.lower(),
            objects=objects or []
        )
        
        word_lower = word.lower()
        if word_lower not in self.vocabulary_entries:
            self.vocabulary_entries[word_lower] = []
        self.vocabulary_entries[word_lower].append(entry)
    
    def add_syntax_pattern(self, pattern: str, verb: str, slots: List[str]):
        """Add a syntax pattern dynamically"""
        self.syntax_patterns.append(SyntaxPattern(
            pattern=pattern,
            verb=verb,
            slots=slots
        ))
    
    def get_vocabulary_matches(self, word: str) -> List[VocabularyEntry]:
        """Get all vocabulary entries matching a word"""
        return self.vocabulary_entries.get(word.lower(), [])
    
    def clear_history(self):
        """Clear command history"""
        self.last_command = None
        self.last_parse_result = None


# Standalone parser functions for testing

def create_parser_from_file(vocab_file: str, syntax_file: str) -> GameParser:
    """Create a parser from vocabulary and syntax files"""
    import json
    
    with open(vocab_file, 'r') as f:
        vocabulary = json.load(f)
    
    with open(syntax_file, 'r') as f:
        syntax_rules = json.load(f)
    
    return GameParser(vocabulary, syntax_rules)


def test_parser():
    """Test parser with sample commands"""
    # Create a test parser with minimal vocabulary
    test_vocab = {
        'words': [
            {'word': 'take', 'type': 'verb', 'canonical': 'take'},
            {'word': 'get', 'type': 'verb', 'canonical': 'take'},
            {'word': 'drop', 'type': 'verb', 'canonical': 'drop'},
            {'word': 'examine', 'type': 'verb', 'canonical': 'examine'},
            {'word': 'x', 'type': 'verb', 'canonical': 'examine'},
            {'word': 'look', 'type': 'verb', 'canonical': 'look'},
            {'word': 'key', 'type': 'noun', 'objects': ['brass_key']},
            {'word': 'brass', 'type': 'adjective'},
            {'word': 'door', 'type': 'noun', 'objects': ['wooden_door']},
            {'word': 'note', 'type': 'noun', 'objects': ['suicide_note']}
        ]
    }
    
    parser = GameParser(test_vocab, [])
    
    # Test various commands
    test_commands = [
        "take key",
        "get the brass key",
        "examine note",
        "x door",
        "look",
        "north",
        "put key in box",
        "go north",
        "i",
        "inventory",
        ""
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        result = parser.parse(cmd)
        print(f"Result: {result}")


if __name__ == "__main__":
    test_parser()