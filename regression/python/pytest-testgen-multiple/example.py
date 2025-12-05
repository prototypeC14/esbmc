def add_positive(a: int, b: int) -> int:
    """Add two positive numbers"""
    assert a > 0 and b > 0, "Both numbers must be positive"
    return a + b

# Test generation mode: use nondet inputs
x = __VERIFIER_nondet_int()
y = __VERIFIER_nondet_int()
add_positive(x, y)
