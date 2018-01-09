# Changes and migration requirements

## Version 0.0.3

* `parse_single_event()` no longer hard-codes the year to 2018 :)  (expedience!)
  * You can use the optional `now` argument to pass in the `datetime` from which
    the year will be extracted.
* Adds function `parse_time_range()`.
