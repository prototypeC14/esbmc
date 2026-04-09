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

Note: The preprocessor rewrites typed nondet_list/nondet_dict calls to
dispatch to the type-specific functions below (e.g. nondet_list(8, nondet_bool())
becomes nondet_bool_list(8)). Each function has a single-type loop body
to avoid frontend type-map confusion from multi-branch models.
"""

# Shared default maximum size for nondet collections
_DEFAULT_NONDET_SIZE: int = 8


def _nondet_size(max_size: int) -> int:
    """Generate a non-deterministic size in range [0, max_size]."""
    size: int = nondet_int()
    __ESBMC_assume(size >= 0)
    __ESBMC_assume(size <= max_size)
    return size


# ── List constructors (one per element type) ──

def nondet_list(max_size: int = _DEFAULT_NONDET_SIZE) -> list:
    """Return a non-deterministic int list."""
    result: list = []
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result.append(nondet_int())
        i = i + 1
    return result


def nondet_float_list(max_size: int = _DEFAULT_NONDET_SIZE) -> list:
    """Return a non-deterministic float list."""
    result: list = []
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result.append(nondet_float())
        i = i + 1
    return result


def nondet_bool_list(max_size: int = _DEFAULT_NONDET_SIZE) -> list:
    """Return a non-deterministic bool list."""
    result: list = []
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result.append(nondet_bool())
        i = i + 1
    return result


def nondet_str_list(max_size: int = _DEFAULT_NONDET_SIZE) -> list:
    """Return a non-deterministic str list."""
    result: list = []
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result.append(nondet_str())
        i = i + 1
    return result


# ── Dict constructors (one per key-value type combination) ──

def nondet_dict(max_size: int = _DEFAULT_NONDET_SIZE) -> dict:
    """Return a non-deterministic int->int dict."""
    result: dict = {}
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result[nondet_int()] = nondet_int()
        i = i + 1
    return result


def nondet_dict_bool_int(max_size: int = _DEFAULT_NONDET_SIZE) -> dict:
    """Return a non-deterministic bool->int dict."""
    result: dict = {}
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result[nondet_bool()] = nondet_int()
        i = i + 1
    return result


def nondet_dict_str_int(max_size: int = _DEFAULT_NONDET_SIZE) -> dict:
    """Return a non-deterministic str->int dict."""
    result: dict = {}
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result[nondet_str()] = nondet_int()
        i = i + 1
    return result


def nondet_dict_int_float(max_size: int = _DEFAULT_NONDET_SIZE) -> dict:
    """Return a non-deterministic int->float dict."""
    result: dict = {}
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result[nondet_int()] = nondet_float()
        i = i + 1
    return result


def nondet_dict_int_bool(max_size: int = _DEFAULT_NONDET_SIZE) -> dict:
    """Return a non-deterministic int->bool dict."""
    result: dict = {}
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result[nondet_int()] = nondet_bool()
        i = i + 1
    return result


def nondet_dict_int_str(max_size: int = _DEFAULT_NONDET_SIZE) -> dict:
    """Return a non-deterministic int->str dict."""
    result: dict = {}
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result[nondet_int()] = nondet_str()
        i = i + 1
    return result


def nondet_dict_str_float(max_size: int = _DEFAULT_NONDET_SIZE) -> dict:
    """Return a non-deterministic str->float dict."""
    result: dict = {}
    size: int = _nondet_size(max_size)
    i: int = 0
    while i < size:
        result[nondet_str()] = nondet_float()
        i = i + 1
    return result
