from common.datetime_utils import create_localized_datetime
from datetime import datetime
from common.enumerable import each_slice
from common.rql import Rql


class TestRqlKwargs:
    """ Test that the Rql object will transform kwargs as expected. """

    def _assert_equal(self, rql, expected):
        assert str(rql).lower() == expected.lower()

    def test_suffixes(self):
        """ Transforms <identifier>=value into '<identifier>=={value}' """
        EXPECTED = [
            Rql(orderid=32), 'orderid==32',
            Rql(orderid__gt=32), 'orderid=gt=32',
            Rql(orderid__ge=32), 'orderid=ge=32',
            Rql(orderid__lt=32), 'orderid=lt=32',
            Rql(orderid__le=32), 'orderid=le=32',
            Rql(orderid__in=32), 'orderid=in=32',
            Rql(orderid__ni=32), 'orderid=out=32',
            Rql(orderid__hv=False), 'orderid=hv=False',
            Rql(orderid__ne=32), 'orderid!=32',
        ]
        for rql, expected in each_slice(2, EXPECTED):
            self._assert_equal(rql, expected)

    def test_ignores_empty_args(self):
        rql = Rql(None, None)
        assert str(rql) == ''

    def test_combining_args_and_kwargs(self):
        """ Combines args and kwargs. """
        self._assert_equal(
            Rql('dog==1;cat!=love', banana__ne=7, time__gt='happy'), 'dog==1;cat!=love;banana!=7;time=gt=happy'
        )

    def test_or_operator(self):
        """ Uses the or operator to combine. """
        self._assert_equal(
            Rql.or_('dog==1;cat!=love', banana__ne=7, time__gt='happy'), '(dog==1;cat!=love),banana!=7,time=gt=happy'
        )

    def test_internal_double_underscore(self):
        """ Should turn into dot notation. """
        self._assert_equal(
            Rql(banana__id__ne=7, time__id='happy'), 'banana.id!=7;time.id==happy'
        )

    def test_casting_datetime(self):
        """ Should cast in isoformat and include timezone if available and _timezone is True. """
        aware_datetime = create_localized_datetime(2020, 3, 10, 12, 22, 7)
        unaware_datetime = datetime(2020, 3, 10, 12, 22, 7)
        EXPECTED = [
            Rql(start__ge=aware_datetime), 'start=ge=2020-03-10T12:22:07+00:00',
            Rql(start__ge=unaware_datetime), 'start=ge=2020-03-10T12:22:07',
            Rql(_timezone=False, start__ge=aware_datetime), 'start=ge=2020-03-10T12:22:07',
            Rql(_timezone=False, start__ge=unaware_datetime), 'start=ge=2020-03-10T12:22:07',
        ]
        for rql, expected in each_slice(2, EXPECTED):
            self._assert_equal(rql, expected)

    def test_create_comparison(self):
        """ Should return an rql string and cast value. """
        aware_datetime = create_localized_datetime(2020, 3, 10, 12, 22, 7)
        rql = Rql(_timezone=False)
        comparison = rql.create_comparison('myfield', Rql.GREATER_THAN_OR_EQUAL, aware_datetime)
        assert isinstance(comparison, str)
        assert comparison == 'myfield=ge=2020-03-10T12:22:07'

    def test_len(self):
        """ Should give a length of the internal string. """
        rql = Rql(start__ge=8)
        str_ = str(rql)
        assert len(rql) == len(str_)

    def test_escaping(self):
        """ Should escape kwarg values. """
        rql = Rql(start__ge='a%b!c(d)e*f=g,h;i')
        assert str(rql) == 'start=ge=a%25b%21c%28d%29e%2Af%3Dg%2Ch%3Bi'

    def test_joining(self):
        """ Should join tuples and lists and properly escape internal values. """
        expected = 'start=in=(1,2,%21%28);end=gt=1,4,2020-03-10T12:22:07+00:00'

        aware_datetime = create_localized_datetime(2020, 3, 10, 12, 22, 7)
        rql = Rql(start__in=[1, 2, '!('], end__gt=[1, 4, aware_datetime])
        assert str(rql) == expected

        rql = Rql(start__in=(1, 2, '!('), end__gt=(1, 4, aware_datetime))
        assert str(rql) == expected
