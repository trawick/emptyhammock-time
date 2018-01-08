import calendar
from datetime import datetime
import re


class BaseToken(object):
    subclasses = []

    @classmethod
    def prep_val(cls, val):
        return val


class Whitespace(BaseToken):
    subclasses = []
    pat = r'^[ \t]+$'


class String(BaseToken):
    subclasses = []
    pat = r'^[A-Za-z]+$'
    values = []

    @classmethod
    def is_it(cls, val):
        return cls.prep_val(val) in cls.values


class Month(String):
    values = [m.lower() for m in calendar.month_name if m != ''] + \
             [m.lower() for m in calendar.month_abbr if m != '']

    @classmethod
    def prep_val(cls, val):
        return val.lower()

    @classmethod
    def get_month_number(cls, val):
        orig_val = val
        val = val.lower()
        for i in (calendar.month_abbr, calendar.month_name):
            for x, m in enumerate(i):
                if m.lower() == val:
                    return x
        raise ValueError('Invalid month "%s"' % orig_val)


class Day(String):
    values = list(calendar.day_name)


class AmPm(String):
    values = ['am', 'pm']

    @classmethod
    def prep_val(cls, val):
        return val.lower()

    @classmethod
    def is_pm(cls, val):
        return val.lower() == 'pm'


String.subclasses.append(Day)
String.subclasses.append(AmPm)
String.subclasses.append(Month)


class Number(BaseToken):
    subclasses = []
    pat = r'^[0-9:]+$'


class Dash(BaseToken):
    subclasses = []
    pat = r'^[-–—]+$'


types = [Whitespace, String, Number, Dash]


def find_type(val):
    for cl in types:
        if re.match(cl.pat, val):
            return cl
    raise ValueError('bad token: "%s"' % val)


def get_token(s):
    chars = iter(s)
    st, val = None, ''
    while True:
        try:
            n = next(chars)
        except StopIteration:
            yield st, val
            break
        if st and re.match(st.pat, val + n):
            val += n
            continue
        if val != '':
            yield st, val
        val = n
        st = find_type(val)


def get_most_specific(t, v):
    for subclass in t.subclasses:
        if subclass.is_it(v):
            return subclass, v
    return t, v


def parse(s):
    tokens = [
        get_most_specific(t, v)
        for t, v in get_token(s)
        if t != Whitespace
    ]
    return tokens


def convert_date(parsed_date):
    month = parsed_date[0]
    day = parsed_date[1]

    month = Month.get_month_number(month[1])
    day = int(day[1])
    return month, day, 2018


def convert_time(s):
    vals = list(map(int, s.split(':')))
    if len(vals) == 1:
        return vals[0], 0
    return vals[0], vals[1]


def convert_times(parsed_time):
    syntax = [t for t, _ in parsed_time]

    if syntax == [Number, Dash, Number, AmPm]:  # e.g. '7-9pm'
        start_hour, start_minute = convert_time(parsed_time[0][1])
        stop_hour, stop_minute = convert_time(parsed_time[2][1])
        if AmPm.is_pm(parsed_time[3][1]):
            start_hour += 12
            stop_hour += 12
        return start_hour, start_minute, stop_hour, stop_minute

    if syntax == [Number, AmPm]:  # e.g. '9pm'
        start_hour, start_minute = convert_time(parsed_time[0][1])
        if AmPm.is_pm(parsed_time[1][1]):
            start_hour += 12
        return start_hour, start_minute, None, None

    raise ValueError('Unhandled time/range')


def combine_date_times(month, day, year, start_hour, start_minute, stop_hour, stop_minute):
    starts_at_naive = datetime(year, month, day, start_hour, start_minute)
    if stop_hour is not None:
        stops_at_naive = datetime(year, month, day, stop_hour, stop_minute)
    else:
        stops_at_naive = None
    return starts_at_naive, stops_at_naive


def parse_single_event(when, local_tz=None):
    parsed = parse(when)

    if [parsed[0][0], parsed[1][0]] != [Month, Number]:
        raise ValueError('Expected date/time string "%s" to start with month and day' % when)

    parsed_date = parsed[:2]
    parsed_time = parsed[2:]

    month, day, year = convert_date(parsed_date)
    times = convert_times(parsed_time)
    starts_at, ends_at = combine_date_times(month, day, year, *times)
    if local_tz is not None:
        starts_at = local_tz.localize(starts_at)
        if ends_at is not None:
            ends_at = local_tz.localize(ends_at)
    return starts_at, ends_at
