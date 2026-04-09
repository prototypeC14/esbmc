"""
Operational model for non-deterministic collection functions in ESBMC Python frontend.

NOTE: The preprocessor (preprocessor.py) expands nondet_list() and nondet_dict()
calls inline BEFORE this model runs. The expanded code generates fresh nondet
values per element/entry and uses concrete sequential keys for dicts to avoid
solver explosion. The model functions below serve as fallback for non-expanded
contexts (e.g. indirect calls) and as documentation of the intended API.

See preprocessor.py _expand_nondet_call() for the actual expansion logic.

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
    result: dict = {}
    size: int = _nondet_size(max_size)

    if key_type is None and value_type is None:
        # Default int->int: use concrete sequential keys (0,1,2,...) so
        # the contains check in the dict model is trivially decidable.
        # A loop with symbolic keys would cause O(N²) solver explosion.
        # Each value is a fresh nondet_int().
        # For typed cases, the preprocessor expands the call with the
        # correct nondet_*() and concrete key type before this runs.
        if size >= 1:
            result[0] = nondet_int()
        if size >= 2:
            result[1] = nondet_int()
        if size >= 3:
            result[2] = nondet_int()
        if size >= 4:
            result[3] = nondet_int()
        if size >= 5:
            result[4] = nondet_int()
        if size >= 6:
            result[5] = nondet_int()
        if size >= 7:
            result[6] = nondet_int()
        if size >= 8:
            result[7] = nondet_int()
        return result

    # Typed case: preprocessor expands this path with correct types.
    # Fallback: original single-entry behavior.
    if key_type is None:
        key_type = nondet_int()
    if value_type is None:
        value_type = nondet_int()
    i: int = 0
    while i < size:
        result[key_type] = value_type
        i = i + 1

    return result