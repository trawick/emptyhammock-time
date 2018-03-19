from datetime import date, datetime
import unittest

import pytz

from e_time import guess_date


TIME_ZONE = 'US/Eastern'
PYTZ_TIME_ZONE = pytz.timezone(TIME_ZONE)


class TestGuessYear(unittest.TestCase):

    def setUp(self):
        self.december_15 = PYTZ_TIME_ZONE.localize(datetime(2018, 12, 15))

    def test_future_date(self):
        d = guess_date(2, 15, now=self.december_15, local_tz=PYTZ_TIME_ZONE)
        self.assertEqual(
            date(2019, 2, 15), d
        )

    def test_past_date(self):
        d = guess_date(11, 15, now=self.december_15, local_tz=PYTZ_TIME_ZONE)
        self.assertEqual(
            date(2018, 11, 15), d
        )
