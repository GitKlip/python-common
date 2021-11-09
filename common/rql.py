
import re
from datetime import datetime

from common.enumerable import compact


class Rql:
    """ A simple pythonic representation of an rql fragment or statement.

    Mainly this allows most rql statements to be specified by using kwargs and
    ensures that most python types are properly cast.

    See COMPARISON_SUFFIXES for valid comparison suffixes.  All other internal
    double underscores are interpreted as a dot.

    RQL as it's used at 3pl central: http://api.3plcentral.com/rels/rql

    rql = Rql(
        'facility.id=13,status=hv=true',
        creationdate__ge=months_ago,
        order__length=31,
    )
    str(rql) # -> '(facility.id==13,status=hv=true);creationdate=ge=months_ago;order.length==31'

    # OR clauses
    Rql.or_(creationdate_ge=months_ago, orderid=31)
    # -> Rql('creationdate=ge=months_ago,orderid==31')

    # Wildcards
    By default, all wildcard chars in _ESCAPE are escaped in predicates and
    that includes asterisks.  For now, if you need to use wildcards, then you
    will need to introduce it as an argument yourself (with proper escapes).
    """
    AND_OPERATOR = ';'
    OR_OPERATOR = ','

    GREATER_THAN = '=gt='
    GREATER_THAN_OR_EQUAL = '=ge='
    LESS_THAN = '=lt='
    LESS_THAN_OR_EQUAL = '=le='
    IN = '=in='
    NOT_IN = '=out='  # similar to SQL "NOT IN"
    HAS_VALUE = '=hv='  # (bool) has value, similar to SQL “IS NOT NULL” or “IS NULL”
    NOT_EQUAL = '!='
    EQUAL = '=='

    RQL_COMPARISON_OPERATORS = [
        GREATER_THAN,
        GREATER_THAN_OR_EQUAL,
        LESS_THAN,
        LESS_THAN_OR_EQUAL,
        IN,
        NOT_IN,
        HAS_VALUE,
        NOT_EQUAL,
        EQUAL,
    ]
    DEFAULT_COMPARISON = EQUAL

    COMPARISON_SUFFIXES = {
        '__gt': GREATER_THAN,
        '__ge': GREATER_THAN_OR_EQUAL,
        '__lt': LESS_THAN,
        '__le': LESS_THAN_OR_EQUAL,
        '__in': IN,
        '__ni': NOT_IN,
        '__hv': HAS_VALUE,
        '__ne':  NOT_EQUAL,
        None: EQUAL,
    }
    DEFAULT_INCLUDE_TIMEZONE = True
    NO_TIMEZONE_FMT = '%Y-%m-%dT%H:%M:%S'
    _ESCAPE = {
        '!': '%21',
        '(': '%28',
        ')': '%29',
        '*': '%2A',
        '=': '%3D',
        ',': '%2C',
        ';': '%3B',
        '%': '%25',
    }
    _ESCAPE_RE = re.compile('|'.join(map(re.escape, _ESCAPE.keys())))

    def __init__(self, *args, **kwargs):
        self._include_timezone = kwargs.pop('_timezone', self.DEFAULT_INCLUDE_TIMEZONE)
        self._statements = compact(args) + self._kwargs_to_statements(**kwargs)

    @staticmethod
    def escape(value):
        return Rql._ESCAPE_RE.sub(lambda match: Rql._ESCAPE[match.group(0)], value)

    @classmethod
    def or_(cls, *args, **kwargs):
        """ Join all rql statements specified by arg or kwarg with OR_OPERATOR

        Note: will parenthesize any statements that embed logical operators
        (before joining by OR_OPERATOR).
        """
        kwarg_statements = [str(Rql(**{key: val})) for key, val in kwargs.items()]
        all_statements = list(args) + kwarg_statements
        enclosed_statements = [
            cls._parenthesize_if_logical_operators(statement) for statement in all_statements
        ]
        return Rql(cls.OR_OPERATOR.join(enclosed_statements))

    def create_comparison(self, field, operator, value):
        """ Returns an Rql statement str.

        Args:
            field (str): The field.
            operator (str): One of RQL_COMPARISON_OPERATORS.
            value (object): The subject of comparison (will be _cast)

        Returns:
            (str): Returns an rql statement string
        """
        return f"{field}{operator}{self._cast(value)}"

    def _cast(self, value):
        if isinstance(value, datetime):
            if self._include_timezone:
                return value.isoformat().replace(' ', 'T')
            else:
                return value.strftime(self.NO_TIMEZONE_FMT)
        elif isinstance(value, (list, tuple)):
            return ",".join([self._cast(item) for item in value])
        else:
            return self.escape(str(value))

    def _kwarg_to_statement(self, key, value):
        if len(key) >= 4 and key[-4:] in self.COMPARISON_SUFFIXES:
            suffix = key[-4:]
            key = key[:-4]
        else:
            suffix = None
        dotted_key = key.replace('__', '.')
        rql_suffix = self.COMPARISON_SUFFIXES[suffix]
        casted_value = self._cast(value)
        if rql_suffix == self.IN and isinstance(value, (list, tuple)):
            casted_value = f"({casted_value})"
        return f"{dotted_key}{rql_suffix}{casted_value}"

    def _kwargs_to_statements(self, **kwargs):
        return [self._kwarg_to_statement(key, val) for key, val in kwargs.items()]

    @classmethod
    def _parenthesize_if_logical_operators(cls, statement):
        """ surrounds in parentheses if there are logical operators. """
        if (cls.AND_OPERATOR in statement) or (cls.OR_OPERATOR in statement):
            return cls._parenthesize(statement)
        else:
            return statement

    @staticmethod
    def _parenthesize(statement):
        """ Parenthesize the statement if it is not already parenthesized. """
        if not statement:
            return statement

        if statement[0] == '(' and statement[-1] == ')':
            return statement
        else:
            return f'({statement})'

    def _parenthesize_or_statements(self, statement):
        """ If it looks like it has 'or' clauses, wrap in parentheses.

        It doesn't hurt anything and it can keep order of operations correct.
        """
        return self._parenthesize(statement) if self.OR_OPERATOR in statement else statement

    def __str__(self):
        return ";".join(map(str, self._statements))

    __repr__ = __str__

    def __len__(self):
        return self.__str__().__len__()
