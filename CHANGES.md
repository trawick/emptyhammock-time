# Changes and migration requirements

## Version 0.0.11

* 12pm/12:30pm/etc. is now supported when parsing time ranges.

## Version 0.0.10

* `parse_repeat_phrase()` now supports phrases like `Fridays 8pm-11pm`.

## Version 0.0.9

* `parse_repeat_phrase()` now supports phrases like `Every other Thursday 8-11pm`.
* `guess_date()` has been added.

### Breaking changes

* `parse_repeat_phrase()`, `parse_single_event()` and `parse_time_range()`
  can (and should) be imported directly from `e_time`.
* `parse_time_range()`'s signature has changed.  It now takes a `datetime.date`
  instead of year/month/day.  For callers that previously passed `None` for year,
  use `guess_date()` to obtain an appropriate date parameter.

## Version 0.0.8

* `parse_single_event()` can handle year in the string

## Version 0.0.7

* 'a' and 'p' are treated like 'am' and 'pm' in phrases like `7p-11p`

## Version 0.0.6

* `parse_repeat_phrase()` now supports phrases like `1st Fridays 8:30pm-12:30am`.
* `parse_repeat_phrase()` is now a generator.  It no longer returns a list.

## Version 0.0.5

* Non-breaking space (\u00A0) treated like other whitespace
* `parse_repeat_phrase()` implemented for some simple phrases.
* `parse()` can return whitespace tokens, when optional arg `ignore_whitespace`
  is `False`

## Version 0.0.4

* Better guessing of the year

## Version 0.0.3

* `parse_single_event()` no longer hard-codes the year to 2018 :)  (expedience!)
  * You can use the optional `now` argument to pass in the `datetime` from which
    the year will be extracted.
* Adds function `parse_time_range()`.
