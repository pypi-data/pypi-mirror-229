"""
Tools to find names (in data, in code, etc.)
"""

from typing import Mapping
from dol import wrap_kvs, filt_iter

# ---------------------------- Finding names in code ----------------------------

import ast

import ast

def extract_names_from_code(code, *, include_locals=False):
    parsed_ast = ast.parse(code)
    
    for node in ast.walk(parsed_ast):
        # Extracting variable names
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Check if we should include local variables
                    if include_locals or not any(isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) for ancestor in ast.walk(node)):
                        yield target.id
                elif isinstance(target, ast.Tuple):  # Handling multiple assignments
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            # Check if we should include local variables
                            if include_locals or not any(isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) for ancestor in ast.walk(node)):
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
    code_sample = """
x = 10
y, z = 5, 6
def func(a, b=10, *args, **kwargs):
    this_is_a_local_variable = 9
lambda p, z: p + z
    """
    result = list(extract_names_from_code(code_sample))
    print(result)
    assert result == ['x', 'y', 'z', 'func', 'a', 'b', 'this_is_a_local_variable', 'p', 'z']
    # TODO: Make this work:
    # result = list(extract_names_from_code(code_sample, include_locals=False))
    # assert result == ['x', 'y', 'z', 'func', 'a', 'b', 'p', 'z']



# ---------------------------- Finding names in data ----------------------------
def target_instance_checker(*target_types):
    """
    Returns a function that checks if an object is an instance of any of the target_types
    """

    def is_target_instance(obj):
        return isinstance(obj, target_types)

    return is_target_instance


# TODO: Refactor to routing (plug-in open-closed architecture)
def yield_names_from_value(
    v, k=None, *, dict_recursion_condition=target_instance_checker(dict)
):
    """
    Yields all the names (keys) in a value (e.g. a dict, a DataFrame, etc.)
    """
    _yield_names_from_value = partial(
        yield_names_from_value, dict_recursion_condition=dict_recursion_condition
    )
    if isinstance(v, dict):
        yield from v
        for k, vv in v.items():
            if dict_recursion_condition(vv):
                yield from _yield_names_from_value(vv, k)
            # yield from yield_names_from_value(vv, k)
    elif isinstance(v, pd.DataFrame):
        yield from v
    elif isinstance(v, Iterable):
        yield from map(_yield_names_from_value, v)
    else:
        yield from ()


def yield_names_from_mapping(mapping: Mapping):
    """
    Yields all the names (keys) in a mapping (dict-like object).
    Often used as ``sorted(set(yield_names_from_mapping(mapping))``.

    >>> mapping = {'c': 1, 'b': {'a': 2, 'd': 3}}
    >>> sorted(set(yield_names_from_mapping(mapping)))
    ['a', 'b', 'c', 'd']
    """
    for k, v in mapping.items():
        yield from yield_names_from_value(v, k)


# But often it's good to have some example values along with the names,
# so it's easier to know what their role is, what to do with them, etc
# So we have the following functions.


# TODO: Refactor to routing (plug-in open-closed architecture)
def yield_kvs_from_value(
    v, k=None, *, dict_recursion_condition=target_instance_checker(dict)
):
    """
    Yields all the key-value pairs in a value (e.g. a dict, a DataFrame, etc.)
    """
    _yield_kvs_from_value = partial(
        yield_kvs_from_value, dict_recursion_condition=dict_recursion_condition
    )
    if isinstance(v, dict):
        for k, vv in v.items():
            if dict_recursion_condition(vv):
                yield from _yield_kvs_from_value(vv, k)
            else:
                yield k, vv
    elif isinstance(v, pd.DataFrame):
        _dict = v.iloc[0].to_dict()
        yield from _yield_kvs_from_value(_dict)
    elif isinstance(v, Iterable):
        yield from map(_yield_kvs_from_value, v)
    else:
        yield from ()


# TODO: ? Use heapq and itertools.groupby to get a dict of unique keys and an example
# value from yield_kvs_from_value outputs
# from heapq import merge
# from itertools import groupby
def unique_kvs_from_mapping(mapping: Mapping):
    """
    Returns a dict of unique keys and an example value from yield_kvs_from_value outputs.
    """
    d = dict()
    for k, v in mapping.items():
        for kk, vv in yield_kvs_from_value(v, k):
            if kk not in d:
                d[kk] = vv
    return d
