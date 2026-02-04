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
        elem_type: Value returned by type constructor for list elements (default: nondet_int()).
                   Supported: nondet_int(), nondet_float(), nondet_bool(), nondet_str()

    Returns:
        list: A list with arbitrary size and contents of specified type.

    Examples:
        x = nondet_list()                                    # int list, size [0, 8]
        x = nondet_list(5)                                   # int list, size [0, 5]
        x = nondet_list(elem_type=nondet_float())            # float list, size [0, 8]
        x = nondet_list(max_size=10, elem_type=nondet_bool())# bool list, size [0, 10]
    """
    # Determine element type from passed value
    use_float: bool = isinstance(elem_type, float)
    use_bool: bool = isinstance(elem_type, bool)
    use_str: bool = isinstance(elem_type, str)

    result: list = []
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        # Generate a NEW nondet element of the same type each iteration
        if use_float:
            elem = nondet_float()
        elif use_bool:
            elem = nondet_bool()
        elif use_str:
            elem = nondet_str()
        else:
            elem = nondet_int()
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
    # Determine key type from passed value
    key_is_str: bool = isinstance(key_type, str)
    key_is_bool: bool = isinstance(key_type, bool)

    # Determine value type from passed value
    val_is_float: bool = isinstance(value_type, float)
    val_is_bool: bool = isinstance(value_type, bool)
    val_is_str: bool = isinstance(value_type, str)

    result: dict = {}
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        # Generate NEW nondet key of the same type each iteration
        if key_is_str:
            key = nondet_str()
        elif key_is_bool:
            key = nondet_bool()
        else:
            key = nondet_int()

        # Generate NEW nondet value of the same type each iteration
        if val_is_float:
            value = nondet_float()
        elif val_is_bool:
            value = nondet_bool()
        elif val_is_str:
            value = nondet_str()
        else:
            value = nondet_int()

        result[key] = value
        i = i + 1

    return result