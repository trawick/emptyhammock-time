from datetime import datetime, timedelta
import unittest

import pytz

from e_time import (
    parse_repeat_phrase, parse_single_event, parse_time_range,
)
from e_time.tokens_and_syntax import (
    parse, AmPm, Comma, Dash, Day, Days, Month, Number, String,
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
        starts_at, ends_at = parse_single_event(
            'january 13 9-11pm', now=not_now, local_tz=PYTZ_TIME_ZONE
        )
        self.assertEqual(
            PYTZ_TIME_ZONE.localize(datetime(not_now.year, 1, 13, 21, 0)),
            starts_at
        )
        self.assertEqual(
            PYTZ_TIME_ZONE.localize(datetime(not_now.year, 1, 13, 23, 0)),
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

    def test_early_next_year(self):
        month = 12
        day = 31
        year = 2017
        starts_at, ends_at = parse_single_event(
            'january 1 9-11:30pm',
            now=datetime(year, month, day, 13, 30)
        )
        self.assertEqual(
            datetime(year + 1, 1, 1, 21, 0),
            starts_at
        )
        self.assertEqual(
            datetime(year + 1, 1, 1, 23, 30),
            ends_at
        )

    def test_late_last_year(self):
        month = 1
        day = 1
        year = 2018
        starts_at, ends_at = parse_single_event(
            'december 31 9-11:30pm',
            now=datetime(year, month, day, 13, 30)
        )
        self.assertEqual(
            datetime(year - 1, 12, 31, 21, 0),
            starts_at
        )
        self.assertEqual(
            datetime(year - 1, 12, 31, 23, 30),
            ends_at
        )

    def test_range_with_year(self):
        month = 1
        day = 1
        year = 2018
        # note that one has '9pm' instead of just '9', and one has comma before year
        for s in ('december 31, 2016 9pm-11:30pm', 'december 31 2016 9-11:30pm'):
            starts_at, ends_at = parse_single_event(
                s,
                now=datetime(year, month, day, 13, 30)
            )
            self.assertEqual(
                datetime(2016, 12, 31, 21, 0),
                starts_at
            )
            self.assertEqual(
                datetime(2016, 12, 31, 23, 30),
                ends_at
            )

    def test_start_time_with_year(self):
        month = 1
        day = 1
        year = 2018
        for s in ('december 31, 2016 9pm', 'december 31 2016 9pm'):
            starts_at, ends_at = parse_single_event(
                s,
                now=datetime(year, month, day, 13, 30)
            )
            self.assertEqual(
                datetime(2016, 12, 31, 21, 0),
                starts_at
            )
            self.assertEqual(
                None,
                ends_at
            )

    def test_bad_string(self):
        with self.assertRaises(ValueError):
            parse_single_event('1 december 31 2017 9-11:30pm')


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
            ('7p-11p', t_7pm, t_11pm),
            ('8pm – 11pm', t_8pm, t_11pm),
            ('8:30 – 9:30 PM', t_830pm, t_930pm),
            ('8pm-12am', t_8pm, t_12am),
            ('9 PM – 12 AM', t_9pm, t_12am),
            ('9p-12a', t_9pm, t_12am),
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
            ('Mondays 8:30pm', (Days, Number, AmPm)),
            ('january 13 9-11pm', (Month, Number, Number, Dash, Number, AmPm)),
            ('january 13, 2018 9-11pm', (Month, Number, Comma, Number, Number, Dash, Number, AmPm)),
            ('9pm', (Number, AmPm)),
            ('9p', (Number, AmPm)),
            ('9 PM - 12 AM', (Number, AmPm, Dash, Number, AmPm)),
            ('7pm-8:30', (Number, AmPm, Dash, Number)),
        )

        for sample, syntax in samples:
            expected_syntax = list(syntax)
            actual = parse(sample)
            actual_syntax = [x for x, _ in actual]
            self.assertEqual(actual_syntax, expected_syntax, 'Checking "%s"' % sample)


class TestRepeatPhrase(unittest.TestCase):

    def test_1(self):
        now = PYTZ_TIME_ZONE.localize(datetime(2018, 3, 5, 19))
        phrase = '1st and 3rd Wednesdays 8:30pm'
        rv = parse_repeat_phrase(
            phrase, timedelta(days=31), local_tz=PYTZ_TIME_ZONE, now=now
        )
        occurrence_1 = PYTZ_TIME_ZONE.localize(datetime(2018, 3, 7, 20, 30))
        occurrence_2 = PYTZ_TIME_ZONE.localize(datetime(2018, 3, 21, 20, 30))
        occurrence_3 = PYTZ_TIME_ZONE.localize(datetime(2018, 4, 4, 20, 30))
        self.assertEqual(
            [
                (occurrence_1, None),
                (occurrence_2, None),
                (occurrence_3, None),
            ],
            list(rv)
        )

    def test_2(self):
        now = PYTZ_TIME_ZONE.localize(datetime(2018, 3, 1, 19))
        phrase = '1st Fridays 8:30pm-12:30am'
        rv = parse_repeat_phrase(
            phrase, timedelta(days=40), local_tz=PYTZ_TIME_ZONE, now=now
        )
        occurrence_1 = PYTZ_TIME_ZONE.localize(datetime(2018, 3, 2, 20, 30))
        occurrence_2 = PYTZ_TIME_ZONE.localize(datetime(2018, 4, 6, 20, 30))
        self.assertEqual(
            [
                (occurrence_1, occurrence_1 + timedelta(hours=4)),
                (occurrence_2, occurrence_2 + timedelta(hours=4)),
            ],
            list(rv)
        )
