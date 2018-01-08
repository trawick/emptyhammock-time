from datetime import datetime
import unittest

from e_time.parser import (
    parse, parse_single_event,
    AmPm, Dash, Day, Month, Number, String
)


class TestSingleEvent(unittest.TestCase):

    def test(self):
        starts_at, ends_at = parse_single_event('january 13 9-11pm')
        self.assertEqual(
            datetime(2018, 1, 13, 21, 0),
            starts_at
        )
        self.assertEqual(
            datetime(2018, 1, 13, 23, 0),
            ends_at
        )

    def test_no_stop_time(self):
        starts_at, ends_at = parse_single_event('january 13 9:45pm')
        self.assertEqual(
            datetime(2018, 1, 13, 21, 45),
            starts_at
        )
        self.assertEqual(
            None,
            ends_at
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
