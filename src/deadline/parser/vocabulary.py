# 7_code_translation/src/deadline/parser/vocabulary.py
"""
Vocabulary management system
Handles word definitions and lookups for the parser
"""

from typing import Dict, List, Optional, Set
from enum import Enum
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WordType(Enum):
    """Types of words in vocabulary"""
    VERB = "verb"
    NOUN = "noun"
    ADJECTIVE = "adjective"
    PREPOSITION = "preposition"
    ARTICLE = "article"
    CONJUNCTION = "conjunction"
    DIRECTION = "direction"
    NUMBER = "number"
    SPECIAL = "special"


class VocabularyEntry:
    """A single vocabulary entry"""
    
    def __init__(self, word: str, word_type: WordType, canonical: str = None, 
                 objects: List[str] = None, synonyms: List[str] = None):
        self.word = word.lower()
        self.word_type = word_type
        self.canonical = canonical or self.word
        self.objects = objects or []
        self.synonyms = synonyms or []


class Vocabulary:
    """
    Manages game vocabulary
    Equivalent to ZIL's vocabulary system
    """
    
    def __init__(self):
        self.words: Dict[str, List[VocabularyEntry]] = {}
        self.verbs: Set[str] = set()
        self.nouns: Set[str] = set()
        self.adjectives: Set[str] = set()
        self.prepositions: Set[str] = set()
        self.directions: Set[str] = set()
        
        # Common articles and conjunctions
        self.articles = {'a', 'an', 'the', 'some'}
        self.conjunctions = {'and', 'then', ','}
        
        # Initialize with basic vocabulary
        self._initialize_basic_vocabulary()
    
    def _initialize_basic_vocabulary(self):
        """Initialize with essential vocabulary"""
        # Directions
        directions = [
            ('north', 'n'), ('south', 's'), ('east', 'e'), ('west', 'w'),
            ('northeast', 'ne'), ('northwest', 'nw'), ('southeast', 'se'), ('southwest', 'sw'),
            ('up', 'u'), ('down', 'd'), ('in', 'enter'), ('out', 'exit')
        ]
        
        for full, short in directions:
            self.add_word(full, WordType.DIRECTION)
            self.add_word(short, WordType.DIRECTION, canonical=full)
            self.directions.add(full)
            self.directions.add(short)
        
        # Common verbs
        verbs = [
            'look', 'examine', 'take', 'get', 'drop', 'put', 'open', 'close',
            'lock', 'unlock', 'read', 'move', 'push', 'pull', 'turn', 'search',
            'inventory', 'save', 'restore', 'quit', 'wait', 'again', 'score',
            'diagnose', 'verbose', 'brief', 'help'
        ]
        
        for verb in verbs:
            self.add_word(verb, WordType.VERB)
            self.verbs.add(verb)
        
        # Common prepositions
        prepositions = [
            'in', 'on', 'at', 'to', 'with', 'from', 'into', 'onto',
            'under', 'behind', 'beside', 'between', 'through', 'about', 'for'
        ]
        
        for prep in prepositions:
            self.add_word(prep, WordType.PREPOSITION)
            self.prepositions.add(prep)
    
    def load_from_file(self, filepath: Path):
        """Load vocabulary from JSON file"""
        try:
            with open(filepath, 'r') as f:
                vocab_data = json.load(f)
            
            for entry_data in vocab_data.get('words', []):
                word_type = WordType[entry_data['type'].upper()]
                self.add_word(
                    word=entry_data['word'],
                    word_type=word_type,
                    canonical=entry_data.get('canonical'),
                    objects=entry_data.get('objects'),
                    synonyms=entry_data.get('synonyms')
                )
            
            logger.info(f"Loaded {len(vocab_data.get('words', []))} vocabulary entries")
            
        except Exception as e:
            logger.error(f"Failed to load vocabulary: {e}")
    
    def add_word(self, word: str, word_type: WordType, canonical: str = None,
                 objects: List[str] = None, synonyms: List[str] = None):
        """Add a word to the vocabulary"""
        entry = VocabularyEntry(word, word_type, canonical, objects, synonyms)
        
        word_lower = word.lower()
        if word_lower not in self.words:
            self.words[word_lower] = []
        
        self.words[word_lower].append(entry)
        
        # Update type-specific sets
        if word_type == WordType.VERB:
            self.verbs.add(word_lower)
        elif word_type == WordType.NOUN:
            self.nouns.add(word_lower)
        elif word_type == WordType.ADJECTIVE:
            self.adjectives.add(word_lower)
        elif word_type == WordType.PREPOSITION:
            self.prepositions.add(word_lower)
        elif word_type == WordType.DIRECTION:
            self.directions.add(word_lower)
    
    def lookup(self, word: str) -> List[VocabularyEntry]:
        """Look up a word in the vocabulary"""
        return self.words.get(word.lower(), [])
    
    def is_verb(self, word: str) -> bool:
        """Check if word is a verb"""
        return word.lower() in self.verbs
    
    def is_noun(self, word: str) -> bool:
        """Check if word is a noun"""
        return word.lower() in self.nouns
    
    def is_adjective(self, word: str) -> bool:
        """Check if word is an adjective"""
        return word.lower() in self.adjectives
    
    def is_preposition(self, word: str) -> bool:
        """Check if word is a preposition"""
        return word.lower() in self.prepositions
    
    def is_direction(self, word: str) -> bool:
        """Check if word is a direction"""
        return word.lower() in self.directions
    
    def is_article(self, word: str) -> bool:
        """Check if word is an article"""
        return word.lower() in self.articles
    
    def is_conjunction(self, word: str) -> bool:
        """Check if word is a conjunction"""
        return word.lower() in self.conjunctions
    
    def get_canonical_form(self, word: str) -> str:
        """Get the canonical form of a word"""
        entries = self.lookup(word)
        if entries:
            return entries[0].canonical
        return word
    
    def get_objects_for_noun(self, noun: str) -> List[str]:
        """Get object IDs associated with a noun"""
        objects = []
        entries = self.lookup(noun)
        for entry in entries:
            if entry.word_type == WordType.NOUN:
                objects.extend(entry.objects)
        return objects