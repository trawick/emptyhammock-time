# Changes and migration requirements

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
