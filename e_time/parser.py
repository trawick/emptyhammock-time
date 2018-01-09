from datetime import datetime, timedelta

from .tokens_and_syntax import (
    Month, Number, Dash, AmPm,
    evaluate_by_syntax, parse
)


# def _get_now(local_tz=None, now=None):
#     now = now or datetime.now()
#     return local_tz.localize(now) if local_tz else now


# XXX stop hard-coding the year
def convert_date(parsed_date):
    month = parsed_date[0]
    day = parsed_date[1]

    month = Month.get_month_number(month[1])
    day = int(day[1])
    return month, day, 2018


def convert_time(s):
    values = list(map(int, s.split(':')))
    if len(values) == 1:
        return values[0], 0
    return values[0], values[1]


# XXX refactor this to combine logic with parse_time_range()
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


def time_range_guts(start_time_value, start_indicator_value, stop_time_value, stop_indicator_value):
    start_hour, start_minute = convert_time(start_time_value)
    if AmPm.is_pm(start_indicator_value):
        start_hour += 12
    elif start_hour == 12:  # 12am
        start_hour = 0
    if stop_time_value is None:
        return start_hour, start_minute, None, None
    stop_hour, stop_minute = convert_time(stop_time_value)
    if AmPm.is_pm(stop_indicator_value):
        stop_hour += 12
    elif stop_hour == 12:  # 12am
        stop_hour = 0
    return start_hour, start_minute, stop_hour, stop_minute


def start_time_only(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[1]
    stop_time_value = None
    stop_indicator_value = None
    return time_range_guts(start_time_value, start_indicator_value, stop_time_value, stop_indicator_value)


def both_times_both_indicators(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[1]
    stop_time_value = values[3]
    stop_indicator_value = values[4]
    return time_range_guts(start_time_value, start_indicator_value, stop_time_value, stop_indicator_value)


def both_times_start_indicator(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[1]
    stop_time_value = values[3]
    stop_indicator_value = values[1]
    return time_range_guts(start_time_value, start_indicator_value, stop_time_value, stop_indicator_value)


def both_times_stop_indicator(tokens):
    values = [token[1] for token in tokens]
    start_time_value = values[0]
    start_indicator_value = values[3]
    stop_time_value = values[2]
    stop_indicator_value = values[3]
    return time_range_guts(start_time_value, start_indicator_value, stop_time_value, stop_indicator_value)


def parse_time_range(month, day, year, time_range, local_tz=None):
    parsed = parse(time_range)
    start_hour, start_minute, stop_hour, stop_minute = evaluate_by_syntax(
        time_range,
        parsed, (
            ([Number, AmPm], start_time_only),
            ([Number, AmPm, Dash, Number, AmPm], both_times_both_indicators),
            ([Number, AmPm, Dash, Number], both_times_start_indicator),
            ([Number, Dash, Number, AmPm], both_times_stop_indicator),
        )
    )
    try:
        start_time = datetime(year, month, day, start_hour, start_minute)
    except ValueError as e:
        raise ValueError('Error parsing time range "%s": %s' % (
            time_range, e
        )) from e
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


# def parse_repeat_phrase(phrase, how_long, local_tz=None, now=None):
#     """
#     :param phrase: "Every Monday 7-9pm", "Every 3rd Tuesday 6-9pm", etc.
#     :param how_long: (timedelta) For how long into the future should
#         occurrences be generated
#     :param local_tz: Optional local timezone (if not provided, naive datetimes
#         will be returned)
#     :param now: Optional current time (if not provided, the current time will
#         be used)
#     :return: iterable of datetime covering all occurrences between now
#         and now + how_long
#     """
