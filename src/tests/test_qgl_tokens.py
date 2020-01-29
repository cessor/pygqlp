from gqlp.terminals import *


class TestLexer:
    def __init__(self, character):
        self._character = character

    def position(self):
        return 0, 0

    def character(self):
        return self._character


def test_match_LeftCurlyBracket():
    lexer = TestLexer('{')
    assert LeftCurlyBracket.match(lexer) == LeftCurlyBracket()


def test_match_RightCurlyBracket():
    lexer = TestLexer('}')
    assert RightCurlyBracket.match(lexer) == RightCurlyBracket()


def test_match_newline():
    lexer = TestLexer('\n')
    assert NewLine.match(lexer) == NewLine()


def test_match_colon():
    lexer = TestLexer(':')
    assert Colon.match(lexer) == Colon()
