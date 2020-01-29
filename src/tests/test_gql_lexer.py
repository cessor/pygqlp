from nose.tools import *

from gqlp import GraphQLLexer
from gqlp.terminals import *

"""
Caveats:
    - When reading in compound tokens, EOF terminates executions.
      That's ok though, because EOF can never happen within
      compounds.

"""


def print_tokens(tokens):
    for t in tokens:
        print(t)


def test_type():
    gql = """
    type Images {
        TEASER: Image
        PORTRAIT: Image
        BANDEROLE: Image
    }
    """

    expected_tokens = [
        NewLine(),
        Name('type'), Name('Images'), LeftCurlyBracket(), NewLine(),
        Name('TEASER'),    Colon(), Name('Image'), NewLine(),
        Name('PORTRAIT'),  Colon(), Name('Image'), NewLine(),
        Name('BANDEROLE'), Colon(), Name('Image'), NewLine(),
        RightCurlyBracket(), NewLine(),
        Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_name():
    gql = """weasel
    """

    expected_tokens = [
        Name('weasel'), NewLine(), Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_name_with_numbers():
    gql = """wea2sel
    """

    expected_tokens = [
        Name('wea2sel'), NewLine(), Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_name_with_undersore():
    gql = """_wea2sel: weas_el
    """

    expected_tokens = [
        Name('_wea2sel'), Colon(), Name('weas_el'), NewLine(), Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_number_integer():
    gql = """1337
    """

    expected_tokens = [
        Number(1337), NewLine(), Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_number_float():
    gql = """3.1415
    """

    expected_tokens = [
        Number(3.1415), NewLine(), Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_negative_number_float():
    gql = """-3.1415
    """

    expected_tokens = [
        Number(-3.1415), NewLine(), Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_comment():
    gql = """
    type Type {
        # This is a comment
        key: value
    }
    """

    expected_tokens = [
        NewLine(),
        Name('type'), Name('Type'), LeftCurlyBracket(), NewLine(),
        Comment('This is a comment'), NewLine(),
        Name('key'),    Colon(), Name('value'), NewLine(),
        RightCurlyBracket(), NewLine(),
        Eof()
    ]

    lexer = GraphQLLexer(gql)
    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_list():
    gql = """
    type Type {
        key: [ value ]
    }
    """

    expected_tokens = [
        NewLine(),
        Name('type'), Name('Type'), LeftCurlyBracket(), NewLine(),
        Name('key'),    Colon(), LeftSquareBracket(), Name(
            'value'), RightSquareBracket(), NewLine(),
        RightCurlyBracket(), NewLine(),
        Eof()
    ]

    lexer = GraphQLLexer(gql)

    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_errors():
    gql = """
    type Type {
        # this is a comment
        % key: value
    }
    """

    lexer = GraphQLLexer(gql)

    try:
        list(lexer)
    except Terminals.UnexpectedCharacter as e:
        assert_equal(e.line, 4)
        assert_equal(e.column, 9)
        assert str(e)


def test_description():
    gql = '''"Hello, World!" '''

    expected_tokens = [
        String('Hello, World!'), Eof()
    ]

    lexer = GraphQLLexer(gql)

    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_description_tripple_quote():
    gql = '''"""Hello, World!""" '''

    expected_tokens = [
        String('Hello, World!'), Eof()
    ]

    lexer = GraphQLLexer(gql)

    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)


def test_descriptions():
    gql = '''
"""
The set of languages supported by `translate`.
"""
enum Language {
  "English"
  EN

  "French"
  FR

  "Chinese"
  CH
}
    '''

    expected_tokens = [
        NewLine(),
        String("The set of languages supported by `translate`."), NewLine(),
        Name('enum'), Name('Language'), LeftCurlyBracket(), NewLine(),
        String('English'), NewLine(),
        Name('EN'), NewLine(), NewLine(),
        String('French'), NewLine(),
        Name('FR'), NewLine(), NewLine(),
        String('Chinese'), NewLine(),
        Name('CH'), NewLine(),
        RightCurlyBracket(), NewLine(),
        Eof()
    ]

    lexer = GraphQLLexer(gql)

    tokens = list(lexer)
    print_tokens(tokens)
    assert_equal(list(tokens), expected_tokens)
