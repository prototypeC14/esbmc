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


def _fresh_nondet(sample: Any) -> Any:
    """
    Generate a fresh non-deterministic value matching the type of sample.
    When sample is None, defaults to nondet_int().

    Uses isinstance to detect the type at translation time, ensuring each
    branch produces a value of a single known type (no type merging conflicts).
    """
    if isinstance(sample, float):
        return nondet_float()
    if isinstance(sample, bool):
        return nondet_bool()
    if isinstance(sample, str):
        return nondet_str()
    return nondet_int()


def nondet_list(max_size: int = _DEFAULT_NONDET_SIZE, elem_type: Any = None) -> list:
    """
    Return a non-deterministic list where each element is a fresh nondet value.

    Args:
        max_size: Maximum size of the list (default: 8).
                  The actual size will be in range [0, max_size].
        elem_type: Value returned by type constructor for list elements (default: nondet_int()).
                   Supported: nondet_int(), nondet_float(), nondet_bool(), nondet_str()

    Returns:
        list: A list with arbitrary size and distinct nondet contents of specified type.
    """
    result: list = []
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        result.append(_fresh_nondet(elem_type))
        i = i + 1

    return result


def nondet_dict(max_size: int = _DEFAULT_NONDET_SIZE,
                key_type: Any = None,
                value_type: Any = None) -> dict:
    """
    Return a non-deterministic dictionary where each entry has fresh nondet key and value.

    Args:
        max_size: Maximum size of the dictionary (default: 8).
                  The actual size will be in range [0, max_size].
        key_type: Value returned by type constructor for dictionary keys (default: nondet_int()).
                  Supported: nondet_int(), nondet_str(), nondet_bool()
        value_type: Value returned by type constructor for dictionary values (default: nondet_int()).
                    Supported: nondet_int(), nondet_float(), nondet_bool(), nondet_str()

    Returns:
        dict: A dictionary with arbitrary size and distinct nondet contents of specified types.

    Examples:
        d = nondet_dict()                    # int->int dict, size [0, 8]
        d = nondet_dict(5)                   # int->int dict, size [0, 5]
        d = nondet_dict(key_type=nondet_str(), value_type=nondet_float())
        d = nondet_dict(max_size=10, key_type=nondet_int(), value_type=nondet_bool())
    """
    result: dict = {}
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        k: Any = _fresh_nondet(key_type)
        v: Any = _fresh_nondet(value_type)
        result[k] = v
        i = i + 1

    return result
