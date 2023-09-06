"""
Making access to names easier.
"""


from typing import Iterable, Callable
from collections import namedtuple


def mk_str_attr_obj(iterable: Iterable, name: str = None, trans: Callable = None):
    """Make an object with given string attributes.

    The purpose of this function is to offer a different option to having to write
    strings in code when specifying a string value when this value should only be
    taken from a fixed set of values, and use tab completion to see the available
    values.

    :param iterable: an iterable of strings
    :param name: the name of the namedtuple

    >>> f = mk_str_attr_obj('date worker offre success')
    >>> f.date
    'date'
    >>> f.worker
    'worker'
    >>> f.does_not_exist
    Traceback (most recent call last):
    ...
    AttributeError: 'AttrObj' object has no attribute 'does_not_exist'


    """
    if isinstance(iterable, str):
        iterable = iterable.split()
    trans = trans or (lambda x: x)
#     iterable = list(map(str.lower, iterable))
    return namedtuple(name or 'AttrObj', list(map(trans, iterable)))(*iterable)
