from .ignore_tokens import IgnoreTokens
from .terminals import *


class KeywordExpected(Exception):
    def __init__(self, actual, expected: str):
        message = (
            f'Expected keyword "{expected}"'
            f' in line {actual.line},'
            f' column {actual.column}.'
            f' but found "{actual}"'
        )
        super().__init__(message)


class UnexpectedToken(Exception):
    def __init__(self, actual, Expected):
        message = (
            f'Unexpected token {actual.__repr__()}'
            f' in line {actual.line},'
            f' column {actual.column}.'
            f' Expected {Expected}'
        )
        super().__init__(message)


# def _match_data_type(self):
#     basic_types = ("String", "Int", "Float", "Boolean", "ID")
#     type_ = self._match(Name)
#     typename = type_.__str__()
#     if not ((typename in basic_types) or (typename in self._complex_types)):
#         raise BasicTypeExpected(type_, basic_types)

class EndOfStream(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self._tokens = list(IgnoreTokens(tokens, [NewLine, Comment]))
        self._index = -1
        self._complex_types = []

    def token(self):
        try:
            return self._tokens[self._index]
        except IndexError:
            raise EndOfStream()

    def consume(self):
        self._index += 1

    def match(self, Token):
        if not self.peek(Token):
            raise UnexpectedToken(self.token(), Expected=Token)
        token = self.token()
        self.consume()
        return token

    def peek(self, Token):
        return isinstance(self.token(), Token)

    def test(self, Token):
        if self.peek(Token):
            self.consume()

    def match_keyword(self, keyword):
        name = self.match(Name)
        if not name.__str__() == keyword:
            raise KeywordExpected(name, keyword)

    def peek_keyword(self, keyword):
        return self.peek(Name) and (self.token().__str__() == keyword)

    def __str__(self):
        return ' '.join(token.__str__() for token in self._lexer)

    def raise_unexpected_token(self, expected):
        raise UnexpectedToken(self.token(), expected)
