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

Note: The preprocessor rewrites nondet_*() type arguments to integer
constants (0=int, 1=float, 2=bool, 3=str) before this model runs.
"""

# Shared default maximum size for nondet collections
_DEFAULT_NONDET_SIZE: int = 8

# Type IDs — must match the preprocessor's _nondet_call_to_type_id mapping
_T_INT: int = 0
_T_FLOAT: int = 1
_T_BOOL: int = 2
_T_STR: int = 3


def _nondet_size(max_size: int) -> int:
    """Generate a non-deterministic size in range [0, max_size]."""
    size: int = nondet_int()
    __ESBMC_assume(size >= 0)
    __ESBMC_assume(size <= max_size)
    return size


def nondet_list(max_size: int = _DEFAULT_NONDET_SIZE, elem_type: int = 0) -> list:
    """
    Return a non-deterministic list where each element is a fresh nondet value.

    Args:
        max_size: Maximum size of the list (default: 8).
        elem_type: Type ID for elements (0=int, 1=float, 2=bool, 3=str).
                   The preprocessor rewrites nondet_int()/float()/bool()/str()
                   to the corresponding integer before this function is called.
    """
    result: list = []
    size: int = _nondet_size(max_size)

    i: int = 0
    if elem_type == _T_FLOAT:
        while i < size:
            result.append(nondet_float())
            i = i + 1
    elif elem_type == _T_BOOL:
        while i < size:
            result.append(nondet_bool())
            i = i + 1
    elif elem_type == _T_STR:
        while i < size:
            result.append(nondet_str())
            i = i + 1
    else:
        while i < size:
            result.append(nondet_int())
            i = i + 1

    return result


def nondet_dict(max_size: int = _DEFAULT_NONDET_SIZE,
                key_type: int = 0,
                value_type: int = 0) -> dict:
    """
    Return a non-deterministic dictionary where each entry has fresh nondet key and value.

    Args:
        max_size: Maximum size of the dictionary (default: 8).
        key_type: Type ID for keys (0=int, 2=bool, 3=str).
        value_type: Type ID for values (0=int, 1=float, 2=bool, 3=str).
                    The preprocessor rewrites nondet_*() to integers.
    """
    result: dict = {}
    size: int = _nondet_size(max_size)

    i: int = 0
    while i < size:
        if key_type == _T_STR:
            k = nondet_str()
        elif key_type == _T_BOOL:
            k = nondet_bool()
        else:
            k = nondet_int()

        if value_type == _T_FLOAT:
            v = nondet_float()
        elif value_type == _T_BOOL:
            v = nondet_bool()
        elif value_type == _T_STR:
            v = nondet_str()
        else:
            v = nondet_int()

        result[k] = v
        i = i + 1

    return result
