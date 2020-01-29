

class IgnoreTokens(object):
    def __init__(self, lexer, tokens):
        self._lexer = lexer
        self._tokens = tokens

    def _should_drop(self, token):
        return any(
            isinstance(token, TokenType) for TokenType in self._tokens
        )

    def __iter__(self):
        for token in self._lexer:
            if self._should_drop(token):
                continue
            yield token
