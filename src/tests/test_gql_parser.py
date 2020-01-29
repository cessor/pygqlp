from nose.tools import *
import string
from gqlp import GraphQLLexer
from gqlp.parser import *
from gqlp.gql import *


def print_schema(schema):
    for type_ in schema._types:
        print(type_.__repr__())
        for field in type_:
            print('  ', field)


def test_parser():
    gql = """
    type Images {
        TEASER: Image
        PORTRAIT: Image
        # Comment
        BANDEROLE: Image
    }"""

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_non_nullable_fields():
    gql = """
    type Images {
        TEASER: Image
        PORTRAIT: Image!
        # Comment
        BANDEROLE: Image
    }"""

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_multiple_types():
    gql = """
    type Images {
        TEASER: Image
        PORTRAIT: Image!
        # Comment
        BANDEROLE: Image
    }

    type Person {
        Name: String
        Age: Int
        # Comment
        BANDEROLE: Image
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 2)
    print_schema(schema)


def test_list():
    gql = """
    type Query {
      quoteOfTheDay: String
      random: Float!
      rollThreeDice: [Int]
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_non_nullable_list():
    gql = """
    type Query {
      quoteOfTheDay: String
      random: Float!
      rollThreeDice: [Int!]
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_non_nullable_list_non_nullable_content():
    gql = """
    type Query {
      rollThreeDice: [Int!]!
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_parse_non_empty_required_list_arguments():
    gql = """
    type Starship {
      id: ID!
      name: String!
      length(unit: LengthUnit = METER): Float
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_parse_gql_enum():
    gql = """
    enum Episode {
      NEWHOPE
      EMPIRE
      JEDI
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_parse_inheritance():
    gql = """
    type Human implements Character {
      id: ID!
      name: String!
      friends: [Character]
      appearsIn: [Episode]!
      starships: [Starship]
      totalCredits: Int
    }

    type Droid implements Character {
      id: ID!
      name: String!
      friends: [Character]
      appearsIn: [Episode]!
      primaryFunction: String
    }

    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 2)
    print_schema(schema)


def test_parse_query_object():
    gql = """
    query DroidById($id: ID!) {
      droid(id: $id) {
        name
      }
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


def test_parse_comment_with_periods():
    gql = """
    type AgeRatingSchema{
        # agerating schema e.g. fsk
        schema: AgeRatingTypes
        # age rating certification or Min age
        certification: String
    }
    """

    parser = Parser(GraphQLLexer(gql))
    schema = Schema.match(parser)
    assert_equal(len(schema._types), 1)
    print_schema(schema)


# interface
# union SearchResult = Human | Droid | Starship
# Fragments
# mutation
# input
# @deprecated
'''
mutation CreateReviewForEpisode($ep: Episode!, $review: ReviewInput!) {
  createReview(episode: $ep, review: $review) {
    stars
    commentary
  }
}
'''


'''
type Query {
  hero: Character
}

type Character {
  name: String
  friends: [Character]
  homeWorld: Planet
  species: Species
}

type Planet {
  name: String
  climate: String
}

type Species {
  name: String
  lifespan: Int
  origin: Planet
}
'''

'''
query HeroNameAndFriends($episode: Episode = JEDI) {
  hero(episode: $episode) {
    name
    friends {
      name
    }
  }
}
'''


# With directives
'''
query Hero($episode: Episode, $withFriends: Boolean!) {
  hero(episode: $episode) {
    name
    friends @include(if: $withFriends) {
      name
    }
  }
}

'''


# Mutations
'''
mutation CreateReviewForEpisode($ep: Episode!, $review: ReviewInput!) {
  createReview(episode: $ep, review: $review) {
    stars
    commentary
  }
}
'''

# With inputs
'''
mutation CreateReviewForEpisode($ep: Episode!, $review: ReviewInput!) {
  createReview(episode: $ep, review: $review) {
    stars
    commentary
  }
}
'''


"""
query {
  repository(owner: "profusion", name: "sgqlc") {
    issues(first: 100) {
      nodes {
        number
        title
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""


# https://graphql.github.io/graphql-spec/draft/#sec-Source-Text.Lexical-Tokens
