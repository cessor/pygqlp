from .terminals import *


class BasicTypeExpected(Exception):
    def __init__(self, actual, expected: str):
        message = (
            f'Expected one of "{expected}"'
            f' in line {actual.line},'
            f' column {actual.column}.'
            f' but found "{actual}"'
        )
        super().__init__(message)


class Argument(object):
    def __init__(self, name, type, default_value):
        self._name = name
        self._type = type
        self._default_value = default_value

    @classmethod
    def match(cls, parser):
        parser.match(LeftBracket)
        name = parser.match(Name)
        parser.match(Colon)
        type_ = parser.match(Name)

        default_value = None
        if parser.peek(Equals):
            parser.match(Equals)
            default_value = parser.match(Name)

        parser.match(RightBracket)

        return Argument(
            name=name,
            type=type_,
            default_value=default_value
        )


class Entity(object):
    def __str__(self):
        return f'{self._name}'

    def __repr__(self):
        return f'<Type: {self._name}>'


class FieldType:
    @classmethod
    def match(cls, parser):
        if parser.peek(LeftSquareBracket):
            return List.match(parser)
        return parser.match(Name)


class Field(Entity):
    def __init__(self, name: Name, type: Name, argument: Argument = None):
        self._name = name
        self._type = type
        self._argument = argument

    def __repr__(self):
        return f'<{self._name}: {self._type}>'

    @classmethod
    def match(cls, parser):
        name = parser.match(Name)

        argument = None
        if parser.peek(LeftBracket):
            argument = Argument.match(parser)

        parser.match(Colon)

        type_ = FieldType.match(parser)

        if parser.peek(ExclamationMark):
            parser.match(ExclamationMark)
            return NonNullableField(
                name=name,
                type=type_,
                argument=argument
            )

        return Field(
            name=name,
            type=type_,
            argument=argument
        )


class List(object):
    def __init__(self, type):
        self._type = type

    def __repr__(self):
        return f'<List:{self._type}>'

    @classmethod
    def match(cls, parser):
        parser.match(LeftSquareBracket)

        type_ = FieldType.match(parser)

        if parser.peek(ExclamationMark):
            parser.match(ExclamationMark)
            parser.match(RightSquareBracket)
            return NonNullableList(type_)

        parser.match(RightSquareBracket)
        return List(type_)


class NonNullableList(List):
    def __repr__(self):
        return f'<List!: {self._type}>'


class NonNullableField(Field):
    def __repr__(self):
        return f'<{self._name}: {self._type}!>'


class FieldList:
    @classmethod
    def match(cls, parser):
        parser.match(LeftCurlyBracket)

        fields = []
        while not parser.peek(RightCurlyBracket):
            fields.append(
                Field.match(parser)
            )

        parser.match(RightCurlyBracket)
        return fields


class Type(Entity):
    def __init__(self, name, fields, parent=None):
        self._name = name
        self._fields = fields
        self._parent = parent

    def __repr__(self):
        t = self.__class__.__name__
        parent = f' ({self._parent})' if self._parent else ''
        return f'<{t}: {self._name}{parent}>'

    def __iter__(self):
        yield from self._fields

    @classmethod
    def match(cls, parser):
        parser.match_keyword('type')
        name = parser.match(Name)

        parent = None
        if parser.peek_keyword('implements'):
            parser.match_keyword('implements')
            parent = parser.match(Name)

        # Todo: Remove
        parser._complex_types.append(name.__str__())
        return cls(
            name=name,
            fields=FieldList.match(parser),
            parent=parent
        )


class Input(Type):
    @classmethod
    def match(cls, parser):
        parser.match_keyword('input')
        name = parser.match(Name)

        parent = None
        if parser.peek_keyword('implements'):
            parser.match_keyword('implements')
            parent = parser.match(Name)

        # Todo: Remove
        parser._complex_types.append(name.__str__())
        return cls(
            name=name,
            fields=FieldList.match(parser),
            parent=parent
        )


class Enum(object):
    def __init__(self, name, items):
        self._name = name
        self._items = self._fields = items

    def __iter__(self):
        yield from self._fields

    @classmethod
    def match(cls, parser):
        parser.match_keyword('enum')
        name = parser.match(Name)
        parser.match(LeftCurlyBracket)

        items = []

        items.append(parser.match(Name))

        while True:
            if parser.peek(RightCurlyBracket):
                break
            items.append(parser.match(Name))

        parser.match(RightCurlyBracket)

        return Enum(name, items)

    def __repr__(self):
        return f'<Enum: {self._name}>'


class Schema(object):
    def __init__(self, types):
        self._types = types

    @classmethod
    def _match_object(cls, keyword, TypeWeasel, parser):
        if parser.peek_keyword(keyword):
            return TypeWeasel.match(parser)

    @classmethod
    def _match_type_weasel(cls, parser):
        WEASEL = {
            'type': Type,
            'enum': Enum,
            'query': Query,
            'input': Input
        }

        for keyword, TypeWeasel in WEASEL.items():
            weasel = cls._match_object(keyword, TypeWeasel, parser)
            if weasel:
                return weasel

        parser.raise_unexpected_token(expected="type, enum, query, input")

    @classmethod
    def match(cls, parser):
        types = []

        parser.consume()
        while not parser.peek(Eof):

            type_weasel = cls._match_type_weasel(parser)

            types.append(
                type_weasel
            )

        return Schema(
            types=types
        )


class Query(object):
    def __init__(self, name, arguments, document):
        self._name = name
        self._arguments = arguments
        self._document = document

    def __iter__(self):
        yield from self._document

    @classmethod
    def match(cls, parser):
        parser.match_keyword('query')
        name = parser.match(Name)

        arguments = QueryArgument.match(parser)

        parser.match(LeftCurlyBracket)

        document = QueryDocument.match(parser)

        parser.match(RightCurlyBracket)
        return Query(
            name, arguments, document
        )


class QueryDocumentSignature(object):
    @classmethod
    def match(cls, parser):

        name = parser.match(Name)

        parser.match(LeftBracket)

        # TBD: More than one param
        name = parser.match(Name)
        parser.match(Colon)
        parser.match(Dollar)
        variable_name = parser.match(Name)

        parser.match(RightBracket)


class QueryProjectionList(object):
    @classmethod
    def match(cls, parser):

        parser.match(LeftCurlyBracket)

        fields = []
        fields.append(parser.match(Name))

        while not parser.peek(RightCurlyBracket):

            if parser.peek(RightCurlyBracket):
                break

            fields.append(
                parser.match(Name)
            )

            if parser.peek(LeftCurlyBracket):
                fields.append(
                    parser.match_query_projection()
                )

        parser.match(RightCurlyBracket)
        return fields


class QueryDocument(object):
    def __init__(self, signature, document):
        self._signature = signature
        self._document = document

    def __iter__(self):
        yield from self._document

    @classmethod
    def match(cls, parser):
        signature = QueryDocumentSignature.match(parser)

        projection = QueryProjectionList.match(parser)

        return QueryDocument(
            signature, projection
        )


class QueryArgument(object):
    def __init__(self, name, type, required, default_value):
        self._name = name
        self._type = type
        self._required = required
        self._default_value = default_value

    @classmethod
    def match(cls, parser):
        parser.match(LeftBracket)

        parser.match(Dollar)
        name = parser.match(Name)
        parser.match(Colon)
        type_ = parser.match(Name)

        required = False
        if parser.peek(ExclamationMark):
            parser.match(ExclamationMark)
            required = True

        default_value = None
        if parser.peek(Equals):
            parser.match(Equals)
            default_value = parser.match(Name)

        parser.match(RightBracket)

        return QueryArgument(
            name=name,
            type=type_,
            required=required,
            default_value=default_value
        )
