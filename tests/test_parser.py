from datetime import date, datetime, timedelta
import unittest

import pytz

from e_time import (
    parse_repeat_phrase, parse_single_event, parse_time_range,
)
from e_time.tokens_and_syntax import (
    parse, AmPm, Comma, Dash, Day, Days, Midnight, Month, Noon, Number, String,
)
from e_time.parser import _guess_year

TIME_ZONE = 'US/Eastern'
PYTZ_TIME_ZONE = pytz.timezone(TIME_ZONE)


class TestSingleEvent(unittest.TestCase):

    def setUp(self):
        self.now = PYTZ_TIME_ZONE.localize(datetime.now())

    def test(self):
        starts_at, ends_at = parse_single_event('january 13 9-11pm')
        # It may decide that January 13 is next year.
        expected_year = _guess_year(1, 13, PYTZ_TIME_ZONE, self.now)
        self.assertIn(
            expected_year,
            [self.now.year, self.now.year + 1]
        )
        self.assertEqual(
            datetime(expected_year, 1, 13, 21, 0),
            starts_at
        )
        self.assertEqual(
            datetime(expected_year, 1, 13, 23, 0),
            ends_at
        )
        not_now = self.now.replace(year=2015, month=1, day=1)
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
        # It may decide that January 13 is next year.
        expected_year = _guess_year(1, 13, PYTZ_TIME_ZONE, self.now)
        self.assertIn(
            expected_year,
            [self.now.year, self.now.year + 1]
        )
        starts_at, ends_at = parse_single_event('january 13 9:45pm')
        self.assertEqual(
            datetime(expected_year, 1, 13, 21, 45),
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

        t_4am = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 4, 0))
        t_12pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 12))
        t_1230pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 12, 30))
        t_2pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 14))
        t_7pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 19))
        t_8pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 20))
        t_830pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 20, 30))
        t_9pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 21))
        t_930pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 21, 30))
        t_11pm = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 23))
        t_12am = PYTZ_TIME_ZONE.localize(datetime(year, month, day, 23) + timedelta(hours=1))
        test_cases = (
            ('noon-2pm', t_12pm, t_2pm),
            ('9pm-midnight', t_9pm, t_12am),
            ('4am-12:30pm', t_4am, t_1230pm),
            ('4a-12:30pm', t_4am, t_1230pm),
            ('12:30p-2pm', t_1230pm, t_2pm),
            ('12:30pm-2pm', t_1230pm, t_2pm),
            ('9pm-12am', t_9pm, t_12am),
            ('9pm', t_9pm, None),
            ('7pm-8:30pm', t_7pm, t_830pm),
            ('7-9 p.m.', t_7pm, t_9pm),
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
                parse_time_range(date(year, month, day), time_range, PYTZ_TIME_ZONE)
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
            ('9pm-Midnight', (Number, AmPm, Dash, Midnight)),
            ('noon-4pm', (Noon, Dash, Number, AmPm)),
        )

        for sample, syntax in samples:
            expected_syntax = list(syntax)
            actual = parse(sample)
            actual_syntax = [x for x, _ in actual]
            self.assertEqual(actual_syntax, expected_syntax, 'Checking "%s"' % sample)


class TestRepeatPhrase(unittest.TestCase):

    def test_with_just_start_time(self):
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

    def test_with_time_range_1(self):
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

    def test_with_time_range_2(self):
        now = PYTZ_TIME_ZONE.localize(datetime(2018, 2, 22, 12))
        phrase = 'Every other Thursday 8-11pm'
        rv = parse_repeat_phrase(
            phrase, timedelta(days=57), local_tz=PYTZ_TIME_ZONE, now=now
        )
        occurrence_1 = PYTZ_TIME_ZONE.localize(datetime(2018, 2, 22, 20, 0))
        occurrence_2 = PYTZ_TIME_ZONE.localize(datetime(2018, 3, 8, 20, 0))
        occurrence_3 = PYTZ_TIME_ZONE.localize(datetime(2018, 3, 22, 20, 0))
        occurrence_4 = PYTZ_TIME_ZONE.localize(datetime(2018, 4, 5, 20, 0))
        occurrence_5 = PYTZ_TIME_ZONE.localize(datetime(2018, 4, 19, 20, 0))
        self.assertEqual(
            [
                (occurrence_1, occurrence_1 + timedelta(hours=3)),
                (occurrence_2, occurrence_2 + timedelta(hours=3)),
                (occurrence_3, occurrence_3 + timedelta(hours=3)),
                (occurrence_4, occurrence_4 + timedelta(hours=3)),
                (occurrence_5, occurrence_5 + timedelta(hours=3)),
            ],
            list(rv)
        )

    def test_every_occurrence(self):
        now = PYTZ_TIME_ZONE.localize(datetime(2018, 2, 22, 12))
        phrase = 'Thursdays 8pm-12am'
        rv = parse_repeat_phrase(
            phrase, timedelta(days=57), local_tz=PYTZ_TIME_ZONE, now=now
        )
        start_times = [
            PYTZ_TIME_ZONE.localize(datetime(2018, 2, 22, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 3, 1, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 3, 8, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 3, 15, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 3, 22, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 3, 29, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 4, 5, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 4, 12, 20, 0)),
            PYTZ_TIME_ZONE.localize(datetime(2018, 4, 19, 20, 0))
        ]
        start_stop_times = [
            (start, start + timedelta(hours=4))
            for start in start_times
        ]
        self.assertEqual(
            start_stop_times,
            list(rv)
        )
