from nose.tools import *
from gqlp.terminals import *
from kazookid import Substitute
from gqlp.ignore_tokens import IgnoreTokens

def test_ignore_tokens():
    lexer = Substitute()
    lexer.yields([
        Number(3.1415),
        NewLine(),
        Comment('Test'),
        Number(3.1415)
    ])

    expected_tokens = [
        Number(3.1415),
        Number(3.1415),
    ]

    # System under Test
    tokens = IgnoreTokens(lexer, tokens=[Comment, NewLine])

    # Assert
    tokens = list(tokens)
    assert_equal(tokens, expected_tokens)