"""
Operational model for non-deterministic collection functions in ESBMC Python frontend.

USAGE:
    # Lists:
    x = nondet_list()                                    # int list, size [0, 8]
    x = nondet_list(5)                                   # int list, size [0, 5]
    x = nondet_list(elem_type=float)                     # float list, size [0, 8]
    x = nondet_list(max_size=10, elem_type=bool)         # bool list, size [0, 10]

    # Dictionaries:
    d = nondet_dict()                                    # int->int dict, size [0, 8]
    d = nondet_dict(5)                                   # int->int dict, size [0, 5]
    d = nondet_dict(key_type=str, value_type=float)
    d = nondet_dict(max_size=10, key_type=int, value_type=bool)
"""

from typing import Any

# Shared default maximum size for nondet collections
_DEFAULT_NONDET_SIZE: int = 8


def _nondet_size(max_size: int) -> int:
    """
    Generate a non-deterministic size in range [0, max_size].

    Args:
        max_size: Maximum size (inclusive).

    Returns:
        int: A non-deterministic integer in [0, max_size].
    """
    size: int = nondet_int()
    __ESBMC_assume(size >= 0)
    __ESBMC_assume(size <= max_size)
    return size


def nondet_list(max_size: int = _DEFAULT_NONDET_SIZE, elem_type: Any = None) -> list:
    """
    Return a non-deterministic list with specified element type.

    Args:
        max_size: Maximum size of the list (default: 8).
                  The actual size will be in range [0, max_size].
        elem_type: Type of list elements (default: int).
                   Supported: int, float, bool, str

    Returns:
        list: A list with arbitrary size and contents of specified type.

    Examples:
        x = nondet_list()                                    # int list, size [0, 8]
        x = nondet_list(5)                                   # int list, size [0, 5]
        x = nondet_list(elem_type=float)                     # float list, size [0, 8]
        x = nondet_list(max_size=10, elem_type=bool)         # bool list, size [0, 10]
    """
    result: list = []
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        if elem_type is None or elem_type == int:
            elem: Any = nondet_int()
        elif elem_type == float:
            elem: Any = nondet_float()
        elif elem_type == bool:
            elem: Any = nondet_bool()
        elif elem_type == str:
            elem: Any = nondet_str()
        else:
            elem: Any = nondet_int()
        result.append(elem)
        i = i + 1

    return result


def nondet_dict(max_size: int = _DEFAULT_NONDET_SIZE,
                key_type: Any = None,
                value_type: Any = None) -> dict:
    """
    Return a non-deterministic dictionary with specified key and value types.

    Args:
        max_size: Maximum size of the dictionary (default: 8).
                  The actual size will be in range [0, max_size].
        key_type: Type of dictionary keys (default: int).
                  Supported: int, str, bool
        value_type: Type of dictionary values (default: int).
                    Supported: int, float, bool, str

    Returns:
        dict: A dictionary with arbitrary size and contents of specified types.

    Examples:
        d = nondet_dict()                              # int->int dict, size [0, 8]
        d = nondet_dict(5)                             # int->int dict, size [0, 5]
        d = nondet_dict(key_type=str, value_type=float)
        d = nondet_dict(max_size=10, key_type=int, value_type=bool)
    """
    result: dict = {}
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        if key_type is None or key_type == int:
            k: Any = nondet_int()
        elif key_type == str:
            k: Any = nondet_str()
        elif key_type == bool:
            k: Any = nondet_bool()
        else:
            k: Any = nondet_int()

        if value_type is None or value_type == int:
            v: Any = nondet_int()
        elif value_type == float:
            v: Any = nondet_float()
        elif value_type == bool:
            v: Any = nondet_bool()
        elif value_type == str:
            v: Any = nondet_str()
        else:
            v: Any = nondet_int()

        result[k] = v
        i = i + 1

    return result
