from .terminals import Terminals


class Lexer(object):
    class EndOfFile(Exception):
        pass

    def __init__(self, graqhql_schema: str, terminals: Terminals):
        self._schema = graqhql_schema
        self._terminals = terminals
        self._index = -1
        self._lines = 0
        self._column = 0
        self._character = None

    def position(self):
        return self._lines + 1, self._column - 1

    def character(self):
        try:
            return self._schema[self._index]
        except IndexError:
            raise self.EndOfFile()

    def consume_while(self, condition):
        buffer_ = []

        buffer_.append(self.character())
        self._consume()

        while condition(self.character()):
            buffer_.append(self.character())
            self._consume()

        self._index -= 1
        return ''.join(buffer_)

    def _increment_line(self):
        self._lines += 1
        self._column = 0

    def _consume(self):
        self._column += 1
        self._index += 1

    def _read(self):
        while True:
            self._consume()
            try:
                token = self._terminals.match(self)
                if token:
                    yield token
            except self._terminals.NewLine as e:
                self._increment_line()
                yield e.token

    def __iter__(self):
        try:
            yield from self._read()
        except self.EndOfFile:
            yield self._terminals.eof()
