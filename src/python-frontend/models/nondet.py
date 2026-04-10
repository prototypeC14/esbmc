"""
Operational model for non-deterministic collection functions in ESBMC Python frontend.

KNOWN LIMITATIONS:

  nondet_list: Cannot be fixed in this file due to ESBMC frontend issues.
    The preprocessor (preprocessor.py::_expand_nondet_call) expands
    nondet_list calls inline as user code, generating fresh nondet values
    per element with correct types. This is necessary because:
      1. Branch type mixing: the frontend processes ALL if/elif branches
         when converting this model file (is_loading_models=true). Multiple
         result.append() calls with different types pollute list_type_map,
         causing "unresolved operand type" errors on element access.
      2. Parameter type erasure: unannotated parameters get type void*,
         so isinstance cannot determine the actual argument type.
         (python_converter.cpp:8069 — arg_type = any_type())
    Only direct assignments (x = nondet_list(...)) are expanded.
    Other contexts (return values, nested expressions) use the model
    function below as fallback (original single-value behavior).

  nondet_dict: Fixed directly in this file using is-None checks.
    The default case (key_type=None, value_type=None) generates fresh
    nondet_int() keys and values each iteration, allowing multiple entries.
    For typed cases, the passed value is reused (original single-entry
    behavior) because isinstance cannot determine the parameter type.
    Note: symbolic keys cause O(N²) solver complexity from the dict model's
    contains/find_index search. Use --unwind 3 for dict tests to keep
    solver performance manageable.

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

    Note: The preprocessor expands this call inline so that each element
    gets a fresh nondeterministic value. This model function body is the
    original (unfixed) fallback for non-expanded contexts. See the
    KNOWN LIMITATIONS note at the top of this file for details.

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

    For the default case (no type args), each iteration generates fresh
    nondet_int() keys and values, allowing the dict to have multiple
    distinct entries. For typed cases, the passed value is reused each
    iteration (single-entry behavior) because isinstance cannot determine
    the parameter type due to frontend type erasure (void*).

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

    i: int = 0
    if key_type is None and value_type is None:
        # Default case: fresh keys and values each iteration.
        while i < size:
            result[nondet_int()] = nondet_int()
            i = i + 1
    else:
        # Typed case: reuse passed values (original single-entry behavior).
        if key_type is None:
            key_type = nondet_int()
        if value_type is None:
            value_type = nondet_int()
        while i < size:
            result[key_type] = value_type
            i = i + 1

    return result
