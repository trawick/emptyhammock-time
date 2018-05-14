""" Logic to split time strings into tokens and determine token types """
import calendar
import re


class IgnoreCase(object):
    """
    Mixin to override default prep_val() method of BaseToken with an
    implementation that converts the input to lower case.
    """
    @classmethod
    def prep_val(cls, val):
        """
        Prepare a string value for determining if it has the form
        represented by this class.

        :param val: the string value to prepare
        :return: prepared form
        """
        return val.lower()


class BaseToken(object):
    """
    Base class for the various token types that can appear in supported
    date/time phrases
    """
    subclasses = []

    @classmethod
    def prep_val(cls, val):
        """
        Prepare a string value for determining if it has the form
        represented by this class.

        :param val: the string value to prepare
        :return: prepared form
        """
        return val


class Comma(BaseToken):
    """
    Match and represent a common in the date/time phrase
    """
    subclasses = []
    pat = r'^,$'


class Whitespace(BaseToken):
    """
    Match and represent whitespace in the date/time phrase
    """
    subclasses = []
    pat = r'^[ \t\u00A0]+$'


class String(BaseToken):
    """
    Match and represent an arbitrary non-numeric string in the date/time phrase
    """
    subclasses = []
    pat = r'^[A-Za-z.]+$'
    values = []

    @classmethod
    def is_it(cls, val):
        """
        Check if a string value has the form represented a particular String
        class/subclass

        :param val: the string to check
        :return: True/False
        """
        return cls.prep_val(val) in cls.values


class Month(IgnoreCase, String):
    """
    Represent a month string
    """
    values = [m.lower() for m in calendar.month_name if m != ''] + \
             [m.lower() for m in calendar.month_abbr if m != '']

    @classmethod
    def get_month_number(cls, val):
        """
        Return month number (1-12) for a month string

        :param val: the month string
        :return: month number 1-12
        """
        orig_val = val
        val = val.lower()
        for month_iterable in (calendar.month_abbr, calendar.month_name):
            for month_num, month_str in enumerate(month_iterable):
                if month_str.lower() == val:
                    return month_num
        raise ValueError('Invalid month "%s"' % orig_val)


class Day(String):
    """
    Represent the singular form of a day of the week (string)
    """
    values = list(calendar.day_name)

    @classmethod
    def get_day_of_week(cls, value):
        """
        Return day number (0-6) for a day string

        :param value: the day string
        :return: day number 0-6
        """
        return cls.values.index(value)


class Days(String):
    """
    Represent the plural form of a day of the week (string)
    """
    values = [
        '%ss' % day_name
        for day_name in calendar.day_name
    ]

    @classmethod
    def get_day_of_week(cls, value):
        """
        Return day number (0-6) for a day string in plural form

        :param value: the day string
        :return: day number 0-6
        """
        return Day.get_day_of_week(value[:-1])


class AmPm(IgnoreCase, String):
    """
    Represent an AM/PM indicator
    """
    am_values = ('am', 'a', 'a.m.', )
    pm_values = ('pm', 'p', 'p.m.', )
    values = am_values + pm_values

    @classmethod
    def is_pm(cls, val):
        """
        Check if the specified string represents the PM indicator

        :param val: the AM/PM string
        :return: True if it represents PM
        """
        return val.lower() in cls.pm_values


class Midnight(IgnoreCase, String):
    """
    Represent the string midnight
    """
    values = ["midnight"]


class Noon(IgnoreCase, String):
    """
    Represent the string noon
    """
    values = ["noon"]


String.subclasses.append(Days)
String.subclasses.append(Day)
String.subclasses.append(AmPm)
String.subclasses.append(Month)
String.subclasses.append(Midnight)
String.subclasses.append(Noon)


class Number(BaseToken):
    """
    Represent a number from datetime strings, including a time like "9:00"
    """
    subclasses = []
    pat = r'^[0-9:]+$'


class Dash(BaseToken):
    """
    Represent dash/hyphen/etc.
    """
    subclasses = []
    pat = r'^[-–—]+$'


TYPES = [Comma, Whitespace, String, Number, Dash]


def _find_type(val):
    for token_type in TYPES:
        if re.match(token_type.pat, val):
            return token_type
    raise ValueError('bad token: "%s"' % val)


def _get_token(string):
    chars = iter(string)
    token_type, token_value = None, ''
    while True:
        try:
            next_char = next(chars)
        except StopIteration:
            yield token_type, token_value
            break
        if token_type and re.match(token_type.pat, token_value + next_char):
            token_value += next_char
            continue
        if token_value != '':
            yield token_type, token_value
        token_value = next_char
        token_type = _find_type(token_value)


def _get_most_specific(token_type, token_value):
    for subclass in token_type.subclasses:
        if subclass.is_it(token_value):
            return subclass, token_value
    return token_type, token_value


def parse(time, ignore_whitespace=True):
    """
    Parse a string of time-related tokens, including
    * general string
    * month name or abbreviation
    * day name
    * am/pm indicator
    * dash/hyphen
    * number (integer or time of day)
    :param time: string to be parsed
    :param ignore_whitespace: whether or not to remove whitespace tokens
        before returning
    :return: sequence of type/value tuples
    """
    tokens = [
        _get_most_specific(token_type, token_value)
        for token_type, token_value in _get_token(time)
        if token_type != Whitespace or not ignore_whitespace
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
