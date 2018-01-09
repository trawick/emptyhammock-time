# emptyhammock-time

## Time-related utilities for Python

### `parse_single_event()`

This function parses a text string describing a single time range, returning
a tuple of start and end times (`datetime.datetime`).  The second time will
be `None` if only one time is specified by the string.

Example string input:

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

## Support

This package exists to support my own commercial activities.  Just maybe it can
provide other developers with a helpful hint, or even more.  Feel free to open
Github issues for suggestions or suspected problems, but please don't expect me
to volunteer any time to respond or otherwise address them directly.  Think of
Github issues for this project as a way to document something you'd like me to
be aware of when fixing problems or implementing future requirements.
