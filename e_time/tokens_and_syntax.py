import calendar
import re


class BaseToken(object):
    subclasses = []

    @classmethod
    def prep_val(cls, val):
        return val


class Comma(BaseToken):
    subclasses = []
    pat = r'^,$'


class Whitespace(BaseToken):
    subclasses = []
    pat = r'^[ \t\u00A0]+$'


class String(BaseToken):
    subclasses = []
    pat = r'^[A-Za-z.]+$'
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

    @classmethod
    def get_day_of_week(cls, value):
        return cls.values.index(value)


class Days(String):
    values = [
        '%ss' % day_name
        for day_name in calendar.day_name
    ]

    @classmethod
    def get_day_of_week(cls, value):
        return Day.get_day_of_week(value[:-1])


class AmPm(String):
    am_values = ('am', 'a', 'a.m.', )
    pm_values = ('pm', 'p', 'p.m.', )
    values = am_values + pm_values

    @classmethod
    def prep_val(cls, val):
        return val.lower()

    @classmethod
    def is_pm(cls, val):
        return val.lower() in cls.pm_values


String.subclasses.append(Days)
String.subclasses.append(Day)
String.subclasses.append(AmPm)
String.subclasses.append(Month)


class Number(BaseToken):
    subclasses = []
    pat = r'^[0-9:]+$'


class Dash(BaseToken):
    subclasses = []
    pat = r'^[-–—]+$'


types = [Comma, Whitespace, String, Number, Dash]


def _find_type(val):
    for cl in types:
        if re.match(cl.pat, val):
            return cl
    raise ValueError('bad token: "%s"' % val)


def _get_token(s):
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
        st = _find_type(val)


def _get_most_specific(t, v):
    for subclass in t.subclasses:
        if subclass.is_it(v):
            return subclass, v
    return t, v


def parse(s, ignore_whitespace=True):
    """
    Parse a string of time-related tokens, including
    * general string
    * month name or abbreviation
    * day name
    * am/pm indicator
    * dash/hyphen
    * number (integer or time of day)
    :param s: string to be parsed
    :param ignore_whitespace: whether or not to remove whitespace tokens
        before returning
    :return: sequence of type/value tuples
    """
    tokens = [
        _get_most_specific(t, v)
        for t, v in _get_token(s)
        if t != Whitespace or not ignore_whitespace
    ]
    return tokens


def evaluate_by_syntax(what_is_being_parsed, tokens, syntax_table):
    """
    Given a tokenized form of what is being parsed, find the handler for it in
    a provided syntax table and invoke the handler.  If no matching syntax is
    found in the syntax table, raise ValueError.

    :param what_is_being_parsed: string repr of what is being parsed, for use
        in exception messages
    :param tokens: sequence of type/value pairs as returned by parse()
    :param syntax_table: sequence of tuples with two elements:
        * type sequence
        * reference to handler function to call when the tokens sequence has
          the same type sequence
    :return: whatever the handlers return
    """
    token_types = [token[0] for token in tokens]
    for expected_types, handler in syntax_table:
        if list(expected_types) == token_types:
            return handler(tokens)
    raise ValueError('Time specification "%s" has unexpected syntax' % what_is_being_parsed)
