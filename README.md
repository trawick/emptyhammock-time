# emptyhammock-time

## Time-related utilities for Python 3

### `parse_repeat_phrase()`

This function parses a text string describing occurrences of an event that
repeats on some or all of a specific day of the week, such as 2nd Fridays
or 1st and 3rd Mondays.

Example input:

* `parse_repeat_phrase('1st Fridays 8:30pm-12:30am', timedelta(days=40))`

It starts with the first occurrence after the current time (or the value
of the optional `now` parameter); it will generate all occurrences from
that time over the range expressed by the 2nd argument.

Normally the optional `local_tz` argument should be set to a `pytz` timezone.

### `parse_single_event()`

This function parses a text string describing a single time range on a
specified date, returning a tuple of start and end times (`datetime.datetime`).
The year will be set to the current year, unless the optional argument `now`
is provided, in which case the year will be extracted from that `datetime`.
The second time will be `None` if only one time is specified by the string.

Example input:

* `parse_single_event('january 13 9-11pm')`
* `parse_single_event('january 13 9:45pm')`

Naive `datetime`s will be returned unless a `pytz` timezone is specified with
the optional parameter `local_tz`:

```python
    import pytz
    from e_time import parse_single_event
    us_eastern = pytz.timezone('US/Eastern')
    starts_at, _ = parse_single_event('january 13 9:45pm', local_tz=us_eastern)
```

### `parse_time_range()`

This function parses a text string describing a single time range, returning
a tuple of start and end times (`datetime.datetime`) for the date specified
in arguments to the function.

Example use with the optional time zone argument:

```python
    import pytz
    from e_time import parse_time_range
    us_eastern = pytz.timezone('US/Eastern')
    starts_at, ends_at = parse_time_range(1, 15, 2018, '9pm-12am', local_tz=us_eastern)
```

## Support

This package exists to support my own commercial activities.  Just maybe it can
provide other developers with a helpful hint, or even more.  Feel free to open
Github issues for suggestions or suspected problems, but please don't expect me
to volunteer any time to respond or otherwise address them directly.  Think of
Github issues for this project as a way to document something you'd like me to
be aware of when fixing problems or implementing future requirements.
