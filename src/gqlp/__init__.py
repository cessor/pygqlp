from .lexer import Lexer
from .terminals import *


class GraphQLLexer(Lexer):
    def __init__(self, graqhql_schema: str):
        grammar = Terminals(
            Eof=Eof,
            NewLine=NewLine,
            Whitespace=Whitespace,
            terminals=[
                Name,
                Number,
                String,
                Comment,
                Colon,
                Equals,
                Dollar,
                ExclamationMark,
                LeftBracket,
                RightBracket,
                LeftCurlyBracket,
                RightCurlyBracket,
                LeftSquareBracket,
                RightSquareBracket
            ]
        )
        super().__init__(graqhql_schema, grammar)
