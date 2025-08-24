# 7_code_translation/tests/test_parser.py
"""Tests for the parser module"""

import pytest
from deadline.parser.parser import GameParser, ParseResult
from deadline.parser.vocabulary import Vocabulary, WordType


class TestParser:
    @pytest.fixture
    def parser(self):
        vocabulary = {
            "words": [
                {"word": "take", "type": "verb", "canonical": "take"},
                {"word": "key", "type": "noun", "objects": ["brass_key"]},
                {"word": "north", "type": "direction"}
            ]
        }
        syntax_rules = [
            {"pattern": "take OBJECT", "verb": "take", "slots": ["direct_object"]}
        ]
        return GameParser(vocabulary, syntax_rules)
    
    def test_parse_simple_command(self, parser):
        result = parser.parse("take key")
        assert result.is_valid
        assert result.verb == "take"
        assert result.direct_object == "brass_key"
    
    def test_parse_direction(self, parser):
        result = parser.parse("north")
        assert result.is_valid
        assert result.verb == "go"
        assert result.direct_object == "north"
    
    def test_parse_invalid(self, parser):
        result = parser.parse("xyzzy")
        assert not result.is_valid