def check_positive(n: int) -> int:
    """Check if a number is positive and return its double"""
    assert n > 0, "Number must be positive"
    return n * 2

# Test generation mode: use nondet inputs
a = __VERIFIER_nondet_int()
check_positive(a)
