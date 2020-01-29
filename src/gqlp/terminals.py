import string


class Token(object):

    def __init__(self, value='', line=0, column=0):
        self._value = value
        self.line = line
        self.column = column

    def __repr__(self):
        value = f': {self._value}' if self._value else ''
        type_ = self.__class__.__name__
        return f'<{type_}{value}>'

    def __eq__(self, other):
        return type(self) == type(other) and self._value == other._value

    @classmethod
    def test(cls, character):
        return character in cls.MATCH

    @classmethod
    def match(cls, lexer):
        if not cls.test(lexer.character()):
            return
        line, column = lexer.position()
        return cls(line=line, column=column)

    def __str__(self):
        return self.MATCH


class CompoundToken(Token):
    FIRST = ''

    @classmethod
    def test_first(cls, character):
        return character in (cls.FIRST or cls.MATCH)

    @classmethod
    def convert(cls, value):
        return value

    @classmethod
    def match(cls, lexer):
        if not cls.test_first(lexer.character()):
            return

        line, column = lexer.position()
        value = lexer.consume_while(cls.test)
        value = cls.convert(value)
        return cls(value, line=line, column=column)

    def __str__(self):
        return str(self._value)


class Whitespace(CompoundToken):
    MATCH = ' \t'


class Name(CompoundToken):
    '''
    Matches: [a-zA-Z][a-zA-Z0-9]+
    '''
    FIRST = string.ascii_letters + '_'
    MATCH = string.digits + FIRST


class Number(CompoundToken):
    '''
    Matches [0-9]+(\..[0-9]+)
    '''
    FIRST = string.digits + '-'
    MATCH = string.digits + '.-'

    @classmethod
    def convert(cls, value):
        if '.' in value:
            return float(value)
        return int(value)


class String(CompoundToken):
    DOUBLE_QUOTE = '\"'

    @classmethod
    def match(cls, lexer):
        if not lexer.character() == cls.DOUBLE_QUOTE:
            return

        # Todo:
        # This does not differentiate between one-lined and
        # multi-lined strings, e.g.,
        # """  -- """ should span over several lines,
        # while " -- " should not, and should actually break when
        # \n is encountered.

        line, column = lexer.position()
        # Read all \"
        lexer.consume_while(lambda c: c == cls.DOUBLE_QUOTE)
        # Swallow newline character
        lexer._consume()
        # Read all text until \" is reached
        value = lexer.consume_while(lambda c: c != cls.DOUBLE_QUOTE)
        # Eat leftover \" characters
        lexer.consume_while(lambda c: c == cls.DOUBLE_QUOTE)
        return cls(value.strip(), line, column)

    def __str__(self):
        return f'"{self._value}"'


class Comment(CompoundToken):
    HASH = '#'

    @classmethod
    def match(cls, lexer):
        if not lexer.character() == cls.HASH:
            return

        line, column = lexer.position()

        # Swallow hash
        lexer._consume()

        value = lexer.consume_while(lambda c: c != '\n')
        return cls(value.strip(), line, column)


class Colon(Token):
    MATCH = ':'


class ExclamationMark(Token):
    MATCH = '!'


class Dollar(Token):
    MATCH = '$'


class NewLine(Token):
    MATCH = '\n'


class LeftSquareBracket(Token):
    MATCH = '['


class RightSquareBracket(Token):
    MATCH = ']'


class LeftBracket(Token):
    MATCH = '('


class RightBracket(Token):
    MATCH = ')'


class Equals(Token):
    MATCH = '='


class LeftCurlyBracket(Token):
    MATCH = '{'


class RightCurlyBracket(Token):
    MATCH = '}'


class Eof(Token):
    def __str__(self):
        return '✔️'


# Todo:
class UnicodeByteOrderMark(Token):
    MATCH = '\uFEFF'


class Terminals(object):
    class NewLine(Exception):
        def __init__(self, token):
            self.token = token
            super().__init__(token)

    class UnexpectedCharacter(Exception):
        def __init__(self, character, line, column):
            self.character = character
            self.line = line
            self.column = column
            message = f'Unexpected character {character} in line {line}, column {column}'
            super().__init__(message)

    def __init__(self, Eof, NewLine: Token, Whitespace: Token, terminals: list):
        self._Eof = Eof
        self._NewLine = NewLine
        self._Whitespace = Whitespace
        self._terminals = terminals

    def eof(self):
        return self._Eof()

    def match(self, lexer):
        if self._Whitespace.match(lexer):
            return

        if self._NewLine.match(lexer):
            raise self.NewLine(self._NewLine())

        for Token in self._terminals:
            token = Token.match(lexer)
            if token:
                return token

        raise self.UnexpectedCharacter(
            lexer.character(),
            *lexer.position()
        )
