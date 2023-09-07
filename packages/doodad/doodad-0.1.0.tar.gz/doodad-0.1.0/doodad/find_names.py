"""
Tools to find names (in data, in code, etc.)
"""

from typing import Mapping, Iterable
from functools import partial
import ast

from dol import wrap_kvs, filt_iter

from doodad.util import target_instance_checker


# TODO: Make it open-closed (plug-in architecture) with routing
# TODO: Make a conditional-on-import-success router
def dflt_value_normalizer(v):
    """
    A default value normalizer that does nothing.
    """
    # return early for most common cases
    if isinstance(v, (Mapping, int, float, bool)):
        return v

    # ... then, try out other border cases
    try:
        return parsed_ast(v)
    except Exception as e:
        pass

    with suppress(Exception):
        import pandas as pd

        if isinstance(v, pd.DataFrame):
            return v.iloc[0].to_dict()

    # If all else fails, just return the value
    return v


# NOTE: Not meant to be used yet, since even default behavior is not quite right.
#  Just meant to be a placeholder for the general idea.
# TODO: This NEEDs to be made into plug-in architecture (routing)
def find_names(src, *, value_normalizer=dflt_value_normalizer):
    """
    Finds all the names (variables, functions, etc.) in a piece of code or data.

    >>> mapping = {'c': 1, 'b': {'a': 2, 'd': 3}}
    >>> list(find_names(mapping))
    ['c', 'b', 'a', 'd']
    >>> import os
    >>> list(find_names(os.path.join))
    ['join', 'a', 'a', 'sep', 'path', 'path']

    """
    src = value_normalizer(src)
    if isinstance(src, ast.AST):
        yield from extract_names_from_code(src)
    else:
        yield from yield_names_from_vk(src)


def parsed_ast(code):
    try:
        parsed_ast = ast.parse(code)
    except Exception as e:
        # If it can't be parsed assume we can get the source code from it and parse that
        import inspect

        obj = code  # code is just some object from which we want the source code
        code_str = inspect.getsource(obj)
        parsed_ast = ast.parse(code_str)
    return parsed_ast


# ---------------------------- Finding names in code ----------------------------


# TODO: Variadic args and kwargs are not extracted correctly
# TODO: Plug-in architecture (routing) to specify what kinds of names to extract
#   (e.g. functions, variables, arguments etc.)
def extract_names_from_code(code, *, include_locals=False):
    """
    Extracts all the names (variables, functions, etc.) from a piece of code.

    In the following example, we extract the names from the ``os.path.join`` function:

    >>> code_string = '''
    ... def foo(a, b=10, *args, **kwargs):
    ...     this_is_a_local_variable = 9
    ...     return a + b
    ... '''
    >>> list(extract_names_from_code(code_string))
    ['foo', 'a', 'b', 'this_is_a_local_variable']

    Could also give a python object directly (as long as the source code can be
    extracted from it through ``inspect.getsource``):
    >>> import os
    >>> list(extract_names_from_code(os.path.join))
    ['join', 'a', 'a', 'sep', 'path', 'path']

    """
    _parsed_ast = parsed_ast(code)

    for node in ast.walk(_parsed_ast):
        # Extracting variable names
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Check if we should include local variables
                    if include_locals or not any(
                        isinstance(
                            ancestor,
                            (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
                        )
                        for ancestor in ast.walk(node)
                    ):
                        yield target.id
                elif isinstance(target, ast.Tuple):  # Handling multiple assignments
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            # Check if we should include local variables
                            if include_locals or not any(
                                isinstance(
                                    ancestor,
                                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
                                )
                                for ancestor in ast.walk(node)
                            ):
                                yield elt.id
        # Extracting function argument names
        elif isinstance(node, ast.FunctionDef):
            yield node.name  # name of the function
            for arg in node.args.args:
                yield arg.arg
        elif isinstance(node, ast.Lambda):
            for arg in node.args.args:
                yield arg.arg


def test_extract_names_from_code():
    # Testing the extract_names_from_code function
    code_sample = '''
x = 10
y, z = 5, 6
def func(a, b=10, *args, **kwargs):
    this_is_a_local_variable = 9
lambda p, z: p + z
    '''
    result = list(extract_names_from_code(code_sample))
    print(result)
    assert result == [
        'x',
        'y',
        'z',
        'func',
        'a',
        'b',
        'this_is_a_local_variable',
        'p',
        'z',
    ]
    # TODO: Make this work:
    # result = list(extract_names_from_code(code_sample, include_locals=False))
    # assert result == ['x', 'y', 'z', 'func', 'a', 'b', 'p', 'z']


# ---------------------------- Finding names in data ----------------------------


# TODO: Refactor to routing (plug-in open-closed architecture). Separate visit logic and yield logic.
#   Is a dol.kv_walk (remap?) pattern.
def yield_names_from_vk(
    v, k=None, *, dict_recursion_condition=target_instance_checker(dict)
):
    """
    Yields all the names (keys) in a value (e.g. a dict, a DataFrame, etc.)

    >>> mapping = {'c': 1, 'b': {'a': [{'apple': 1}, {'banana': 2}], 'b': 3}}
    >>> list(yield_names_from_vk(mapping))
    ['c', 'b', 'a', 'b']
    """
    _yield_names_from_vk = partial(
        yield_names_from_vk, dict_recursion_condition=dict_recursion_condition
    )
    if isinstance(v, dict):
        yield from v
        for k, vv in v.items():
            if dict_recursion_condition(vv):
                yield from _yield_names_from_vk(vv, k)
            # yield from yield_names_from_vk(vv, k)
    # elif isinstance(v, pd.DataFrame):
    #     yield from v
    elif isinstance(v, Iterable):
        yield from map(_yield_names_from_vk, v)
    else:
        yield from ()


def yield_names_from_mapping(mapping: Mapping):
    """
    Yields all the names (keys) in a mapping (dict-like object).
    Often used as ``sorted(set(yield_names_from_mapping(mapping))``.

    >>> mapping = {'c': 1, 'b': {'a': 2, 'd': 3}}
    >>> sorted(set(yield_names_from_mapping(mapping)))
    ['a', 'd']
    """
    for k, v in mapping.items():
        yield from yield_names_from_vk(v, k)


# But often it's good to have some example values along with the names,
# so it's easier to know what their role is, what to do with them, etc
# So we have the following functions.


# TODO: Refactor to routing (plug-in open-closed architecture)
# TODO: Even this hard coded behavior sucks. At least change them
def yield_names_and_values_from_vk(
    v, k=None, *, dict_recursion_condition=target_instance_checker(dict),
):
    """
    Yields all the key-value pairs in a value (e.g. a dict, a DataFrame, etc.)

    >>> mapping = {'c': 1, 'b': {'a': 2, 'd': 3}}
    >>> list(yield_names_and_values_from_vk(mapping))
    [('c', 1), ('a', 2), ('d', 3)]
    """
    _yield_names_and_values_from_vk = partial(
        yield_names_and_values_from_vk,
        dict_recursion_condition=dict_recursion_condition,
    )
    if isinstance(v, Mapping):
        for k, vv in v.items():
            if dict_recursion_condition(vv):
                yield from _yield_names_and_values_from_vk(vv, k)
            elif isinstance(k, str):
                yield k, vv
    elif isinstance(v, Iterable):
        yield from map(_yield_names_and_values_from_vk, v)
    else:
        yield from ()


from contextlib import suppress


# TODO: ? Use heapq and itertools.groupby to get a dict of unique keys and an example
# value from yield_names_and_values_from_vk outputs
# from heapq import merge
# from itertools import groupby
def unique_kvs_from_mapping(
    mapping: Mapping, *, value_normalizer=dflt_value_normalizer
):
    """
    Returns a dict of unique keys and an example value from yield_names_and_values_from_vk outputs.
    """
    d = dict()
    for k, v in mapping.items():
        v = value_normalizer(v)
        for kk, vv in yield_names_and_values_from_vk(v, k):
            if kk not in d:
                d[kk] = vv
    return d
