""" Implementation of API functions for parsing time strings """
from datetime import date, datetime, timedelta

from .tokens_and_syntax import (
    AmPm, Comma, Dash, Day, Days, evaluate_by_syntax, Midnight, Month, Noon,
    Number, parse, String, Whitespace,
)


def _get_now(local_tz=None, now=None):
    if now:
        return now
    now = datetime.now()
    return local_tz.localize(now) if local_tz else now


def _guess_year(month, day, local_tz, now):
    now = _get_now(local_tz, now)
    # If using now.year doesn't work due to leap year considerations,
    # we couldn't guess the year anyway.
    then = datetime(now.year, month, day)
    then = local_tz.localize(then) if local_tz else then
    delta = timedelta(days=9*30)
    if now - then > delta:
        return now.year + 1
    if then - now > delta:
        return now.year - 1
    return now.year


def guess_date(month, day, local_tz=None, now=None):
    """
    guess_date() builds a date from the provided month and day by guessing the
    year.

    :param month:
    :param day:
    :param local_tz:
    :param now:
    :return: datetime.date with the provided month and day and the guessed year.
    """
    year = _guess_year(month, day, local_tz, now)
    return date(year, month, day)


def _convert_date(parsed_date, local_tz=None, now=None):
    month = parsed_date[0]
    day = parsed_date[1]

    month = Month.get_month_number(month[1])
    day = int(day[1])

    if len(parsed_date) > 2:
        year = int(parsed_date[-1][1])
    else:
        year = _guess_year(month, day, local_tz, now)

    return month, day, year


def _convert_time(time):
    values = list(map(int, time.split(':')))
    if len(values) == 1:
        return values[0], 0
    return values[0], values[1]


def _combine_date_times(month, day, year, start_hour, start_minute, stop_hour, stop_minute):
    starts_at_naive = datetime(year, month, day, start_hour, start_minute)
    if stop_hour is not None:
        stops_at_naive = datetime(year, month, day, stop_hour, stop_minute)
    else:
        stops_at_naive = None
    return starts_at_naive, stops_at_naive


def parse_single_event(when, local_tz=None, now=None):
    """
    This function parses a text string describing a single time range on a
    specified date, returning a tuple of start and end times
    (datetime.datetime). The year will be set to the current year, unless the
    optional argument now is provided, in which case the year will be extracted
    from that datetime. The second time will be None if only one time is
    specified by the string.

    Example:

    import pytz
    from e_time import parse_single_event
    us_eastern = pytz.timezone('US/Eastern')
    starts_at, _ = parse_single_event('january 13 9:45pm', local_tz=us_eastern)
    starts_at, ends_at = parse_single_event('january 13 9-11pm', local_tz=us_eastern)

    :param when: string representing the event date and time or time range
    :param local_tz: optional pytz time zone, for building localized times
    :param now: optional datetime from which the year will be extracted
    :return: datetime for start time, None or datetime for stop time
    """
    parsed = parse(when)

    syntax = [t for t, _ in parsed]

    # Parsed fields better be some number of date fields followed by time
    # time fields (and nothing else); check for allowed syntaxes, and find
    # the split between date and time fields.
    num_date_field_table = (
        ([Month, Number, Number, Dash, Number, AmPm], 2),
        ([Month, Number, Number, AmPm], 2),
        ([Month, Number, Number, Number, Dash, Number, AmPm], 3),
        ([Month, Number, Number, Number, AmPm, Dash, Number, AmPm], 3),
        ([Month, Number, Number, Number, AmPm], 3),
        ([Month, Number, Comma, Number, Number, Dash, Number, AmPm], 4),
        ([Month, Number, Comma, Number, Number, AmPm, Dash, Number, AmPm], 4),
        ([Month, Number, Comma, Number, Number, AmPm], 4),
    )

    for if_syntax, then_num_date_fields in num_date_field_table:
        if syntax == if_syntax:
            num_date_fields = then_num_date_fields
            break
    else:
        raise ValueError('Date/time string "%s" has unexpected syntax' % when)

    parsed_date = parsed[:num_date_fields]
    parsed_time = parsed[num_date_fields:]

    month, day, year = _convert_date(parsed_date, local_tz=local_tz, now=now)
    times = _get_start_stop_hour_minute(parsed_time, when)
    starts_at, ends_at = _combine_date_times(month, day, year, *times)
    if local_tz is not None:
        starts_at = local_tz.localize(starts_at)
        if ends_at is not None:
            ends_at = local_tz.localize(ends_at)
    return starts_at, ends_at


def _to_24hr(indicator, hour):
    if AmPm.is_pm(indicator):
        if hour != 12:
            hour += 12
    elif hour == 12:  # 12am
        hour = 0
    return hour


def _get_time_range(
        start_time_value, start_indicator_value, stop_time_value=None, stop_indicator_value=None
):
    start_hour, start_minute = _convert_time(start_time_value)
    start_hour = _to_24hr(start_indicator_value, start_hour)
    if stop_time_value is None:
        return start_hour, start_minute, None, None
    stop_hour, stop_minute = _convert_time(stop_time_value)
    stop_hour = _to_24hr(stop_indicator_value, stop_hour)
    return start_hour, start_minute, stop_hour, stop_minute


def _start_time_only(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[1]
    return _get_time_range(start_time_value, start_indicator_value)


def _both_times_both_indicators(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[1]
    stop_time_value = values[3]
    stop_indicator_value = values[4]
    return _get_time_range(
        start_time_value, start_indicator_value, stop_time_value, stop_indicator_value
    )


def _both_times_start_indicator(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[1]
    stop_time_value = values[3]
    stop_indicator_value = values[1]
    return _get_time_range(
        start_time_value, start_indicator_value, stop_time_value, stop_indicator_value
    )


def _both_times_stop_indicator(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[3]
    stop_time_value = values[2]
    stop_indicator_value = values[3]
    return _get_time_range(
        start_time_value, start_indicator_value, stop_time_value, stop_indicator_value
    )


def _start_time_noon(tokens):
    values = [token[1] for token in tokens]
    start_time_value = "12"
    start_indicator_value = "pm"
    stop_time_value = values[2]
    stop_indicator_value = values[3]
    return _get_time_range(
        start_time_value, start_indicator_value, stop_time_value, stop_indicator_value
    )


def _stop_time_midnight(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[1]
    stop_time_value = "12"
    stop_indicator_value = "am"
    return _get_time_range(
        start_time_value, start_indicator_value, stop_time_value, stop_indicator_value
    )


def _get_start_stop_hour_minute(parsed, time_range):
    return evaluate_by_syntax(
        time_range,
        parsed, (
            ([Number, AmPm], _start_time_only),
            ([Number, AmPm, Dash, Number, AmPm], _both_times_both_indicators),
            ([Number, AmPm, Dash, Number], _both_times_start_indicator),
            ([Number, Dash, Number, AmPm], _both_times_stop_indicator),
            ([Number, AmPm, Dash, Midnight], _stop_time_midnight),
            ([Noon, Dash, Number, AmPm], _start_time_noon),
        )
    )


def parse_time_range(on_date, time_range, local_tz=None):
    """
    This function parses a text string describing a single time range,
    returning a tuple of start and end times (datetime.datetime) for the date
    specified in arguments to the function.

    Example:

    from datetime import date
    import pytz
    from e_time import parse_time_range
    us_eastern = pytz.timezone('US/Eastern')

    starts_at, ends_at = parse_time_range(date(2018, 1, 15), '9pm-12am', local_tz=us_eastern)

    :param on_date: datetime.date indicating the applicable date
    :param time_range: string representing the time range
    :param local_tz: optional pytz time zone, for building localized times
    :return: datetime for start time, None or datetime for stop time
    """
    year, month, day = on_date.year, on_date.month, on_date.day
    parsed = parse(time_range)
    start_hour, start_minute, stop_hour, stop_minute = \
        _get_start_stop_hour_minute(parsed, time_range)
    try:
        start_time = datetime(year, month, day, start_hour, start_minute)
    except ValueError as ex:
        raise ValueError('Error parsing time range "%s": %s' % (
            time_range, ex
        )) from ex
    if local_tz:
        start_time = local_tz.localize(start_time)

    if stop_hour is not None:
        stop_time = datetime(year, month, day, stop_hour, stop_minute)
        if local_tz:
            stop_time = local_tz.localize(stop_time)
        if stop_time < start_time:
            stop_time += timedelta(days=1)
    else:
        stop_time = None

    return start_time, stop_time


class _DaysRepeatPerWeekOfMonth(object):
    """
    Generate repeated days, where the basis of the repetition is a certain week
    of the month (e.g., first and third Fridays).
    """

    def __init__(self, day_of_week, occurrences_of_day, time_range):
        self.day_of_week = day_of_week[0].get_day_of_week(day_of_week[1])  # can be Day or Days
        self.occurrences_of_day = [int(x) for _, x in occurrences_of_day]
        self.time_range = time_range

    def get_occurrences(self, how_long, local_tz, now):
        """
        Generate datetimes representing the repetition

        :param how_long:
        :param local_tz:
        :param now:
        :return:
        """
        current = _get_now(local_tz, now)
        last = current + how_long
        while current < last:
            if current.weekday() == self.day_of_week:
                # Okay, it is the correct day of the week, but it might not be the right occurrence.
                for occurrence in self.occurrences_of_day:
                    max_dom = 7 * occurrence  # 3rd Monday can't be later than 21st
                    min_dom = max_dom - 6  # or earlier than 15th
                    if min_dom <= current.day <= max_dom:
                        # It is happening today!
                        yield current.month, current.day, current.year

            current += timedelta(days=1)


class _DaysRepeatPerWeek(object):
    """
    Generate repeated days, where the basis of the repetition is relative
    to weeks since the prior repetition (e.g., every other Monday).
    """

    def __init__(self, day_of_week, days_between, time_range):
        self.day_of_week = day_of_week[0].get_day_of_week(day_of_week[1])  # can be Day or Days
        self.days_between = days_between
        self.time_range = time_range

    def get_occurrences(self, how_long, local_tz, now):
        """
        Generate datetimes representing the repetition

        :param how_long:
        :param local_tz:
        :param now:
        :return:
        """
        current = _get_now(local_tz, now)
        last = current + how_long

        while current < last:
            if current.weekday() == self.day_of_week:
                break
            current += timedelta(days=1)
        else:
            return  # no occurrences

        while current < last:
            yield current.month, current.day, current.year
            current += timedelta(days=self.days_between)


def _repeat_phrase_1(tokens):
    values = [token[1] for token in tokens]
    assert len(values[1]) == len(values[6]) == 2  # 'st', 'nd', 'rd', etc.
    assert values[3] == 'and'
    repeat = _DaysRepeatPerWeekOfMonth(
        tokens[8],
        [tokens[0], tokens[5]],
        values[10] + values[11],
    )
    return repeat


def _repeat_phrase_2(tokens):
    values = [token[1] for token in tokens]
    assert len(values[1]) == 2  # 'st', 'nd', 'rd', etc.
    repeat = _DaysRepeatPerWeekOfMonth(
        tokens[3],
        [tokens[0]],
        values[5] + values[6] + values[7] + values[8] + values[9],
    )
    return repeat


def _repeat_phrase_3(tokens):
    values = [token[1] for token in tokens]
    assert values[0].lower() == 'every'
    assert values[2].lower() == 'other'
    repeat = _DaysRepeatPerWeek(
        tokens[4],
        14,  # "every other" === "every 14 days",
        values[6] + values[7] + values[8] + values[9]
    )
    return repeat


def _repeat_phrase_4(tokens):
    values = [token[1] for token in tokens]
    repeat = _DaysRepeatPerWeek(
        tokens[0],
        7,  # every === "every 7 days",
        ''.join(values[2:]),
    )
    return repeat


def parse_repeat_phrase(phrase, how_long, local_tz=None, now=None):
    """
    :param phrase: "1st and 3rd Wednesdays 8:30pm", etc.
    :param how_long: (timedelta) For how long into the future should
        occurrences be generated
    :param local_tz: Optional local timezone (if not provided, naive datetimes
        will be returned)
    :param now: Optional current time (if not provided, the current time will
        be used)
    :return: iterable of tuples of begin/end datetime covering all occurrences
        between now and now + how_long
    """
    parsed = parse(phrase, ignore_whitespace=False)
    repeat = evaluate_by_syntax(
        phrase,
        parsed, (
            # '1st and 3rd Wednesdays 8:30pm'
            (
                [
                    Number, String, Whitespace, String, Whitespace, Number,
                    String, Whitespace, Days, Whitespace, Number, AmPm
                ],
                _repeat_phrase_1,
            ),
            # '1st Fridays 8:30pm-12:30am'
            (
                [
                    Number, String, Whitespace, Days, Whitespace,
                    Number, AmPm, Dash, Number, AmPm,
                ],
                _repeat_phrase_2,
            ),
            # 'Every other Thursday 8-11pm'
            (
                [
                    String, Whitespace, String, Whitespace, Day, Whitespace,
                    Number, Dash, Number, AmPm
                ],
                _repeat_phrase_3,
            ),
            # 'Thursdays 8pm-12am'
            (
                [
                    Days, Whitespace,
                    Number, AmPm, Dash, Number, AmPm,
                ],
                _repeat_phrase_4,
            ),
        ),
    )

    for month, day, year in repeat.get_occurrences(how_long, local_tz, now):
        yield parse_time_range(
            date(year, month, day), repeat.time_range, local_tz,
        )
