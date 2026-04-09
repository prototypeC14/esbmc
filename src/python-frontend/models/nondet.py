"""
Operational model for non-deterministic collection functions in ESBMC Python frontend.

IMPORTANT: The functions below are NOT called directly. The preprocessor
(preprocessor.py::_expand_nondet_call) expands nondet_list/nondet_dict
calls inline before this model runs. This is necessary because ESBMC's
frontend has three limitations that prevent a correct fix in this file:
  1. Parameter type erasure: untyped params become void*, breaking isinstance
  2. Branch mixing: all if/elif branches are processed, polluting list_type_map
  3. Symbolic key explosion: dict[nondet()] triggers O(N²) solver comparisons
The preprocessor bypasses all three by generating type-correct inline code.
See _expand_nondet_call() for the actual expansion logic.

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
        elem_type: Value returned by type constructor for list elements (default: nondet_int()).
                   Supported: nondet_int(), nondet_float(), nondet_bool(), nondet_str()
    
    Returns:
        list: A list with arbitrary size and contents of specified type.
    """
    # Default to nondet_int if no type specified
    if elem_type is None:
        elem_type = nondet_int()

    result: list = []
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        result.append(elem_type)
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
        key_type: Value returned by type constructor for dictionary keys (default: nondet_int()).
                  Supported: nondet_int(), nondet_str(), nondet_bool()
        value_type: Value returned by type constructor for dictionary values (default: nondet_int()).
                    Supported: nondet_int(), nondet_float(), nondet_bool(), nondet_str()

    Returns:
        dict: A dictionary with arbitrary size and contents of specified types.

    Examples:
        d = nondet_dict()                    # int->int dict, size [0, 8]
        d = nondet_dict(5)                   # int->int dict, size [0, 5]
        d = nondet_dict(key_type=nondet_str(), value_type=nondet_float())
        d = nondet_dict(max_size=10, key_type=nondet_int(), value_type=nondet_bool())
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