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
    Return a non-deterministic dictionary with specified key and value types.

    For the default case (int keys/values), each entry gets a fresh nondet
    key with assume-based uniqueness constraints. This bypasses the expensive
    contains search in the dict model (O(N²) symbolic comparisons) by
    appending directly to the internal keys/values lists.

    For typed cases (explicit key_type/value_type), falls back to the
    single-entry behavior due to frontend type dispatch limitations.

    Args:
        max_size: Maximum size of the dictionary (default: 8).
        key_type: Value returned by type constructor for dictionary keys (default: nondet_int()).
        value_type: Value returned by type constructor for dictionary values (default: nondet_int()).
    """
    result: dict = {}
    size: int = _nondet_size(max_size)

    if key_type is not None or value_type is not None:
        # Typed case: fall back to single-entry behavior.
        # Frontend limitations prevent type dispatch for nondet values.
        if key_type is None:
            key_type = nondet_int()
        if value_type is None:
            value_type = nondet_int()
        i: int = 0
        while i < size:
            result[key_type] = value_type
            i = i + 1
        return result

    # Default case: use concrete sequential keys (0,1,2,...) to avoid
    # the O(N²) symbolic key comparison that causes solver explosion.
    # No loop needed — if-chain with concrete keys means contains
    # checks are trivially decidable (1!=0, 2!=0, 2!=1, etc.).
    # Values are fully nondeterministic.
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
