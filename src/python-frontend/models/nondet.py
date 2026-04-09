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

    # Default case: fresh int keys/values via direct append.
    # Skips contains search; uniqueness guaranteed by __ESBMC_assume.
    k0: int = nondet_int()
    k1: int = nondet_int()
    k2: int = nondet_int()
    k3: int = nondet_int()
    k4: int = nondet_int()
    k5: int = nondet_int()
    k6: int = nondet_int()
    k7: int = nondet_int()
    if size >= 1:
        result.keys().append(k0)
        result.values().append(nondet_int())
    if size >= 2:
        __ESBMC_assume(k1 != k0)
        result.keys().append(k1)
        result.values().append(nondet_int())
    if size >= 3:
        __ESBMC_assume(k2 != k0)
        __ESBMC_assume(k2 != k1)
        result.keys().append(k2)
        result.values().append(nondet_int())
    if size >= 4:
        __ESBMC_assume(k3 != k0)
        __ESBMC_assume(k3 != k1)
        __ESBMC_assume(k3 != k2)
        result.keys().append(k3)
        result.values().append(nondet_int())
    if size >= 5:
        __ESBMC_assume(k4 != k0)
        __ESBMC_assume(k4 != k1)
        __ESBMC_assume(k4 != k2)
        __ESBMC_assume(k4 != k3)
        result.keys().append(k4)
        result.values().append(nondet_int())
    if size >= 6:
        __ESBMC_assume(k5 != k0)
        __ESBMC_assume(k5 != k1)
        __ESBMC_assume(k5 != k2)
        __ESBMC_assume(k5 != k3)
        __ESBMC_assume(k5 != k4)
        result.keys().append(k5)
        result.values().append(nondet_int())
    if size >= 7:
        __ESBMC_assume(k6 != k0)
        __ESBMC_assume(k6 != k1)
        __ESBMC_assume(k6 != k2)
        __ESBMC_assume(k6 != k3)
        __ESBMC_assume(k6 != k4)
        __ESBMC_assume(k6 != k5)
        result.keys().append(k6)
        result.values().append(nondet_int())
    if size >= 8:
        __ESBMC_assume(k7 != k0)
        __ESBMC_assume(k7 != k1)
        __ESBMC_assume(k7 != k2)
        __ESBMC_assume(k7 != k3)
        __ESBMC_assume(k7 != k4)
        __ESBMC_assume(k7 != k5)
        __ESBMC_assume(k7 != k6)
        result.keys().append(k7)
        result.values().append(nondet_int())

    return result
