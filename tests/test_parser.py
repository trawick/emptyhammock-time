from datetime import datetime, timedelta
import unittest

import pytz

from e_time.parser import (
    parse, parse_single_event, parse_time_range,
)
from e_time.tokens_and_syntax import (
    AmPm, Dash, Day, Month, Number, String,
)

TIME_ZONE = 'US/Eastern'
PYTZ_TIME_ZONE = pytz.timezone(TIME_ZONE)


class TestSingleEvent(unittest.TestCase):

    def setUp(self):
        self.now = PYTZ_TIME_ZONE.localize(datetime.now())

    def test(self):
        starts_at, ends_at = parse_single_event('january 13 9-11pm')
        self.assertEqual(
            datetime(self.now.year, 1, 13, 21, 0),
            starts_at
        )
        self.assertEqual(
            datetime(self.now.year, 1, 13, 23, 0),
            ends_at
        )
        not_now = self.now.replace(year=2015, day=1)
        starts_at, ends_at = parse_single_event('january 13 9-11pm', now=not_now)
        self.assertEqual(
            datetime(not_now.year, 1, 13, 21, 0),
            starts_at
        )
        self.assertEqual(
            datetime(not_now.year, 1, 13, 23, 0),
            ends_at
        )

    def test_no_stop_time(self):
        starts_at, ends_at = parse_single_event('january 13 9:45pm')
        self.assertEqual(
            datetime(self.now.year, 1, 13, 21, 45),
            starts_at
        )
        self.assertEqual(
            None,
            ends_at
        )


class TestTimeRange(unittest.TestCase):

    def test_em(self):
        now = PYTZ_TIME_ZONE.localize(datetime.now())
        month = 12
        day = 31
        year = now.year

        t_7pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 19))
        t_8pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 20))
        t_830pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 20, 30))
        t_9pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 21))
        t_930pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 21, 30))
        t_11pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 23))
        t_12am = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 23) + timedelta(hours=1))
        test_cases = (
            ('9pm-12am', t_9pm, t_12am),
            ('9pm', t_9pm, None),
            ('7pm-8:30pm', t_7pm, t_830pm),
            ('7pm-8:30', t_7pm, t_830pm),
            ('8:00 pm - 11:00 pm', t_8pm, t_11pm),
            ('7pm-11pm', t_7pm, t_11pm),
            ('8pm – 11pm', t_8pm, t_11pm),
            ('8:30 – 9:30 PM', t_830pm, t_930pm),
            ('8pm-12am', t_8pm, t_12am),
            ('9 PM – 12 AM', t_9pm, t_12am),
        )
        for time_range, expected_starts_at, expected_ends_at in test_cases:
            actual_starts_at, actual_ends_at = \
                parse_time_range(month, day, year, time_range, PYTZ_TIME_ZONE)
            self.assertEqual(
                expected_starts_at, actual_starts_at,
                'Determining starts_at failed for %s' % time_range
            )
            self.assertEqual(
                expected_ends_at, actual_ends_at,
                'Determining ends_at failed for %s' % time_range
            )


class TestTokenizing(unittest.TestCase):

    def test(self):
        samples = (
            ('Dec 29 7-9pm', (Month, Number, Number, Dash, Number, AmPm)),
            ('dec 31 7pm-9', (Month, Number, Number, AmPm, Dash, Number)),
            ('Every Monday 7-9pm', (String, Day, Number, Dash, Number, AmPm)),
            ('january 13 9-11pm', (Month, Number, Number, Dash, Number, AmPm)),
            ('9pm', (Number, AmPm)),
            ('9 PM - 12 AM', (Number, AmPm, Dash, Number, AmPm)),
            ('7pm-8:30', (Number, AmPm, Dash, Number)),
        )

        for sample, syntax in samples:
            expected_syntax = list(syntax)
            actual = parse(sample)
            actual_syntax = [x for x, _ in actual]
            self.assertEqual(actual_syntax, expected_syntax, 'Checking "%s"' % sample)
