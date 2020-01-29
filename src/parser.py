from pathlib import Path
from gqlp import GraphQLLexer
from gqlp.parser import Parser
from gqlp.gql import Schema

def main(_, path):
    parser = Parser(
        GraphQLLexer(Path(path).read_text()),
    )

    schema = Schema.match(parser)
    for type_ in schema._types:
        print(type_.__repr__())
        for field in type_:
            print('  ', field.__repr__())

if __name__ == '__main__':
    import sys
    main(*sys.argv)