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
    Return a non-deterministic list with specified element type.

    Note: The preprocessor expands this call inline so that each element
    gets a fresh nondeterministic value. This model body is kept as
    fallback for non-expanded contexts.

    Args:
        max_size: Maximum size of the list (default: 8).
        elem_type: Value returned by type constructor for list elements (default: nondet_int()).
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
    Return a non-deterministic dictionary where each entry has fresh nondet key and value.

    Each key-value type combination has its own dedicated loop to avoid
    type merging issues in the frontend. The is-None check handles the
    default case; isinstance handles typed arguments; the else fallback
    defaults to nondet_int() when isinstance cannot resolve the type.

    Args:
        max_size: Maximum size of the dictionary (default: 8).
        key_type: Value returned by type constructor for dictionary keys (default: nondet_int()).
        value_type: Value returned by type constructor for dictionary values (default: nondet_int()).
    """
    result: dict = {}
    size: int = _nondet_size(max_size)

    i: int = 0
    if key_type is None:
        if value_type is None:
            while i < size:
                result[nondet_int()] = nondet_int()
                i = i + 1
        elif isinstance(value_type, float):
            while i < size:
                result[nondet_int()] = nondet_float()
                i = i + 1
        elif isinstance(value_type, bool):
            while i < size:
                result[nondet_int()] = nondet_bool()
                i = i + 1
        elif isinstance(value_type, str):
            while i < size:
                result[nondet_int()] = nondet_str()
                i = i + 1
        else:
            while i < size:
                result[nondet_int()] = nondet_int()
                i = i + 1
    elif isinstance(key_type, bool):
        if value_type is None:
            while i < size:
                result[nondet_bool()] = nondet_int()
                i = i + 1
        elif isinstance(value_type, float):
            while i < size:
                result[nondet_bool()] = nondet_float()
                i = i + 1
        elif isinstance(value_type, bool):
            while i < size:
                result[nondet_bool()] = nondet_bool()
                i = i + 1
        elif isinstance(value_type, str):
            while i < size:
                result[nondet_bool()] = nondet_str()
                i = i + 1
        else:
            while i < size:
                result[nondet_bool()] = nondet_int()
                i = i + 1
    elif isinstance(key_type, str):
        if value_type is None:
            while i < size:
                result[nondet_str()] = nondet_int()
                i = i + 1
        elif isinstance(value_type, float):
            while i < size:
                result[nondet_str()] = nondet_float()
                i = i + 1
        elif isinstance(value_type, bool):
            while i < size:
                result[nondet_str()] = nondet_bool()
                i = i + 1
        elif isinstance(value_type, str):
            while i < size:
                result[nondet_str()] = nondet_str()
                i = i + 1
        else:
            while i < size:
                result[nondet_str()] = nondet_int()
                i = i + 1
    else:
        if value_type is None:
            while i < size:
                result[nondet_int()] = nondet_int()
                i = i + 1
        elif isinstance(value_type, float):
            while i < size:
                result[nondet_int()] = nondet_float()
                i = i + 1
        elif isinstance(value_type, bool):
            while i < size:
                result[nondet_int()] = nondet_bool()
                i = i + 1
        elif isinstance(value_type, str):
            while i < size:
                result[nondet_int()] = nondet_str()
                i = i + 1
        else:
            while i < size:
                result[nondet_int()] = nondet_int()
                i = i + 1

    return result
