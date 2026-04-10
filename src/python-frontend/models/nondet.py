"""
Operational model for non-deterministic collection functions in ESBMC Python frontend.

USAGE:
    # Lists:
    x = nondet_list()                                    # int list, size [0, 8]
    x = nondet_list(5)                                   # int list, size [0, 5]
    x = nondet_list(elem_type=nondet_float())                 # float list, size [0, 8]
    x = nondet_list(max_size=10, elem_type=nondet_bool())     # bool list, size [0, 10]

    # Dictionaries:
    d = nondet_dict()                                    # int->int dict, size [0, 8]
    d = nondet_dict(5)                                   # int->int dict, size [0, 5]
    d = nondet_dict(key_type=nondet_str(), value_type=nondet_float())
    d = nondet_dict(max_size=10, key_type=nondet_int(), value_type=nondet_bool())
"""

from typing import Any

# Shared default maximum size for nondet collections
_DEFAULT_NONDET_SIZE: int = 8


def _nondet_size(max_size: int) -> int:
    """Generate a non-deterministic size in range [0, max_size]."""
    size: int = nondet_int()
    __ESBMC_assume(size >= 0)
    __ESBMC_assume(size <= max_size)
    return size


def nondet_list(max_size: int = _DEFAULT_NONDET_SIZE, elem_type: Any = None) -> list:
    """
    Return a non-deterministic list where each element is a fresh nondet value.

    Type dispatch: is-None for default, isinstance for typed args.
    Each branch has a dedicated loop calling the correct nondet function.
    """
    result: list = []
    size: int = _nondet_size(max_size)

    i: int = 0
    if elem_type is None:
        while i < size:
            result.append(nondet_int())
            i = i + 1
    elif isinstance(elem_type, float):
        while i < size:
            result.append(nondet_float())
            i = i + 1
    elif isinstance(elem_type, bool):
        while i < size:
            result.append(nondet_bool())
            i = i + 1
    elif isinstance(elem_type, str):
        while i < size:
            result.append(nondet_str())
            i = i + 1
    else:
        while i < size:
            result.append(nondet_int())
            i = i + 1

    return result


def nondet_dict(max_size: int = _DEFAULT_NONDET_SIZE,
                key_type: Any = None,
                value_type: Any = None) -> dict:
    """
    Return a non-deterministic dictionary where each entry has fresh nondet key and value.

    Type dispatch: is-None for default, isinstance for typed args.
    Each key-value type combination has a dedicated loop.
    """
    # Default to nondet_int if no types specified
    if key_type is None:
        key_type = nondet_int()
    if value_type is None:
        value_type = nondet_int()

    result: dict = {}
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        result[key_type] = value_type
        i = i + 1

    return result
