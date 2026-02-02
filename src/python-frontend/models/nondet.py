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
        elem_type: Ignored (kept for API compatibility). Each element is nondet_int().

    Returns:
        list: A list with arbitrary size and nondet int contents.
    """
    result: list = []
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        # Generate a NEW nondet element for each iteration
        elem: int = nondet_int()
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
        key_type: Ignored (kept for API compatibility). Each key is nondet_int().
        value_type: Ignored (kept for API compatibility). Each value is nondet_int().

    Returns:
        dict: A dictionary with arbitrary size and nondet int keys/values.

    Examples:
        d = nondet_dict()      # int->int dict, size [0, 8]
        d = nondet_dict(5)     # int->int dict, size [0, 5]
    """
    result: dict = {}
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        # Generate NEW nondet key and value for each iteration
        key: int = nondet_int()
        value: int = nondet_int()
        result[key] = value
        i = i + 1

    return result