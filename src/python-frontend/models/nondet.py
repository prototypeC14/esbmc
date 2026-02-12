"""
Operational model for non-deterministic collection functions in ESBMC Python frontend.

USAGE:
    # Lists:
    x = nondet_list()                                    # int list, size [0, 8]
    x = nondet_list(5)                                   # int list, size [0, 5]
    x = nondet_list(elem_type=nondet_float())            # float list, size [0, 8]
    x = nondet_list(max_size=10, elem_type=nondet_bool())# bool list, size [0, 10]

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
        elem_type: A nondet value indicating desired element type (default: int).
                   Pass nondet_int(), nondet_float(), nondet_bool(), or nondet_str().

    Returns:
        list: A list with arbitrary size and contents of specified type.

    Examples:
        x = nondet_list()                                    # int list, size [0, 8]
        x = nondet_list(5)                                   # int list, size [0, 5]
        x = nondet_list(elem_type=nondet_float())            # float list, size [0, 8]
        x = nondet_list(max_size=10, elem_type=nondet_bool())# bool list, size [0, 10]
    """
    result: list = []
    size: int = _nondet_size(max_size)

    # Use isinstance() to detect type, use different variable names per type
    # (ESBMC requires each variable to have a single type across all branches)
    if elem_type is None or isinstance(elem_type, int):
        i: int = 0
        while i < size:
            elem_int: int = nondet_int()
            result.append(elem_int)
            i = i + 1
    elif isinstance(elem_type, float):
        i: int = 0
        while i < size:
            elem_float: float = nondet_float()
            result.append(elem_float)
            i = i + 1
    elif isinstance(elem_type, bool):
        i: int = 0
        while i < size:
            elem_bool: bool = nondet_bool()
            result.append(elem_bool)
            i = i + 1
    elif isinstance(elem_type, str):
        i: int = 0
        while i < size:
            elem_str: str = nondet_str()
            result.append(elem_str)
            i = i + 1
    else:
        i: int = 0
        while i < size:
            elem_default: int = nondet_int()
            result.append(elem_default)
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
        key_type: A nondet value indicating desired key type (default: int).
                  Pass nondet_int(), nondet_str(), or nondet_bool().
        value_type: A nondet value indicating desired value type (default: int).
                    Pass nondet_int(), nondet_float(), nondet_bool(), or nondet_str().

    Returns:
        dict: A dictionary with arbitrary size and contents of specified types.

    Examples:
        d = nondet_dict()                              # int->int dict, size [0, 8]
        d = nondet_dict(5)                             # int->int dict, size [0, 5]
        d = nondet_dict(key_type=nondet_str(), value_type=nondet_float())
        d = nondet_dict(max_size=10, key_type=nondet_int(), value_type=nondet_bool())
    """
    result: dict = {}
    size: int = _nondet_size(max_size)

    # Use isinstance() to detect type, use different variable names per type
    # (ESBMC requires each variable to have a single type across all branches)

    # int keys
    if key_type is None or isinstance(key_type, int):
        if value_type is None or isinstance(value_type, int):
            i: int = 0
            while i < size:
                k_int_v_int_k: int = nondet_int()
                k_int_v_int_v: int = nondet_int()
                result[k_int_v_int_k] = k_int_v_int_v
                i = i + 1
        elif isinstance(value_type, float):
            i: int = 0
            while i < size:
                k_int_v_float_k: int = nondet_int()
                k_int_v_float_v: float = nondet_float()
                result[k_int_v_float_k] = k_int_v_float_v
                i = i + 1
        elif isinstance(value_type, bool):
            i: int = 0
            while i < size:
                k_int_v_bool_k: int = nondet_int()
                k_int_v_bool_v: bool = nondet_bool()
                result[k_int_v_bool_k] = k_int_v_bool_v
                i = i + 1
        elif isinstance(value_type, str):
            i: int = 0
            while i < size:
                k_int_v_str_k: int = nondet_int()
                k_int_v_str_v: str = nondet_str()
                result[k_int_v_str_k] = k_int_v_str_v
                i = i + 1
        else:
            i: int = 0
            while i < size:
                k_int_v_def_k: int = nondet_int()
                k_int_v_def_v: int = nondet_int()
                result[k_int_v_def_k] = k_int_v_def_v
                i = i + 1

    # str keys
    elif isinstance(key_type, str):
        if value_type is None or isinstance(value_type, int):
            i: int = 0
            while i < size:
                k_str_v_int_k: str = nondet_str()
                k_str_v_int_v: int = nondet_int()
                result[k_str_v_int_k] = k_str_v_int_v
                i = i + 1
        elif isinstance(value_type, float):
            i: int = 0
            while i < size:
                k_str_v_float_k: str = nondet_str()
                k_str_v_float_v: float = nondet_float()
                result[k_str_v_float_k] = k_str_v_float_v
                i = i + 1
        elif isinstance(value_type, bool):
            i: int = 0
            while i < size:
                k_str_v_bool_k: str = nondet_str()
                k_str_v_bool_v: bool = nondet_bool()
                result[k_str_v_bool_k] = k_str_v_bool_v
                i = i + 1
        elif isinstance(value_type, str):
            i: int = 0
            while i < size:
                k_str_v_str_k: str = nondet_str()
                k_str_v_str_v: str = nondet_str()
                result[k_str_v_str_k] = k_str_v_str_v
                i = i + 1
        else:
            i: int = 0
            while i < size:
                k_str_v_def_k: str = nondet_str()
                k_str_v_def_v: int = nondet_int()
                result[k_str_v_def_k] = k_str_v_def_v
                i = i + 1

    # bool keys
    elif isinstance(key_type, bool):
        if value_type is None or isinstance(value_type, int):
            i: int = 0
            while i < size:
                k_bool_v_int_k: bool = nondet_bool()
                k_bool_v_int_v: int = nondet_int()
                result[k_bool_v_int_k] = k_bool_v_int_v
                i = i + 1
        elif isinstance(value_type, float):
            i: int = 0
            while i < size:
                k_bool_v_float_k: bool = nondet_bool()
                k_bool_v_float_v: float = nondet_float()
                result[k_bool_v_float_k] = k_bool_v_float_v
                i = i + 1
        elif isinstance(value_type, bool):
            i: int = 0
            while i < size:
                k_bool_v_bool_k: bool = nondet_bool()
                k_bool_v_bool_v: bool = nondet_bool()
                result[k_bool_v_bool_k] = k_bool_v_bool_v
                i = i + 1
        elif isinstance(value_type, str):
            i: int = 0
            while i < size:
                k_bool_v_str_k: bool = nondet_bool()
                k_bool_v_str_v: str = nondet_str()
                result[k_bool_v_str_k] = k_bool_v_str_v
                i = i + 1
        else:
            i: int = 0
            while i < size:
                k_bool_v_def_k: bool = nondet_bool()
                k_bool_v_def_v: int = nondet_int()
                result[k_bool_v_def_k] = k_bool_v_def_v
                i = i + 1

    # default: int keys
    else:
        if value_type is None or isinstance(value_type, int):
            i: int = 0
            while i < size:
                k_def_v_int_k: int = nondet_int()
                k_def_v_int_v: int = nondet_int()
                result[k_def_v_int_k] = k_def_v_int_v
                i = i + 1
        elif isinstance(value_type, float):
            i: int = 0
            while i < size:
                k_def_v_float_k: int = nondet_int()
                k_def_v_float_v: float = nondet_float()
                result[k_def_v_float_k] = k_def_v_float_v
                i = i + 1
        elif isinstance(value_type, bool):
            i: int = 0
            while i < size:
                k_def_v_bool_k: int = nondet_int()
                k_def_v_bool_v: bool = nondet_bool()
                result[k_def_v_bool_k] = k_def_v_bool_v
                i = i + 1
        elif isinstance(value_type, str):
            i: int = 0
            while i < size:
                k_def_v_str_k: int = nondet_int()
                k_def_v_str_v: str = nondet_str()
                result[k_def_v_str_k] = k_def_v_str_v
                i = i + 1
        else:
            i: int = 0
            while i < size:
                k_def_v_def_k: int = nondet_int()
                k_def_v_def_v: int = nondet_int()
                result[k_def_v_def_k] = k_def_v_def_v
                i = i + 1

    return result
