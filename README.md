# emptyhammock-time

[![Build Status](https://travis-ci.org/trawick/emptyhammock-time.svg?branch=master)](https://travis-ci.org/trawick/emptyhammock-time)

## Time-related utilities for Python 3

The included functions parse text that describes a time, time range, or
repeated occurrences of a time.

Examples of text that can be parsed with the appropriate function:

* `1st and 3rd Mondays 7pm-9pm`
* `january 13 3:45pm`
* `9pm-12am`

Each function has an optional `local_tz` argument that should be set to
a `pytz` timezone in most cases.  (Otherwise a naive `datetime` is returned.)

### `parse_repeat_phrase()`

This function parses a text string describing occurrences of an event that
repeats on some or all of a specific day of the week, such as *2nd Fridays*
or *1st and 3rd Mondays* or *Every other Tuesday*.

Example:

```python
import pytz
from datetime import timedelta
from e_time import parse_repeat_phrase
us_eastern = pytz.timezone('US/Eastern')
for begin, end in parse_repeat_phrase('1st Fridays 8:30pm-12:30am',
        timedelta(days=120), local_tz=us_eastern):
    print('{}-{}'.format(begin, end))
```

It starts with the first occurrence after the current time (or after the time
specified by the optional `now` parameter); it will generate all occurrences
from that time over the range expressed by the 2nd argument.

### `parse_single_event()`

This function parses a text string describing a single time range on a
specified date, returning a tuple of start and end times (`datetime.datetime`).
The year will be set to the current year, unless the optional argument `now`
is provided, in which case the year will be extracted from that `datetime`.
The second time will be `None` if only one time is specified by the string.

Example:

```python
import pytz
from e_time import parse_single_event
us_eastern = pytz.timezone('US/Eastern')
starts_at, _ = parse_single_event('january 13 9:45pm', local_tz=us_eastern)
starts_at, ends_at = parse_single_event('january 13 9-11pm', local_tz=us_eastern)
```

### `parse_time_range()`

This function parses a text string describing a single time range, returning
a tuple of start and end times (`datetime.datetime`) for the date specified
in arguments to the function.

Example:

```python
from datetime import date
import pytz
from e_time import parse_time_range
us_eastern = pytz.timezone('US/Eastern')

starts_at, ends_at = parse_time_range(date(2018, 1, 15), '9pm-12am', local_tz=us_eastern)
```

## Dependencies

* Python 3.5 or higher
* Optional: `pytz`, for constructing time zones to pass to the library

## Support

Please open Github issues for suggestions or suspected problems.  Even if I am
unable to respond in a timely basis, the information may quickly become valuable
to others, and I will eventually find time to respond to the issue.
