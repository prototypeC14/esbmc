def check_sign(n: int) -> int:
    """Check if a number is positive or negative."""
    if n > 0:
        return 1
    else:
        return -1

# This will trigger an assertion failure
result = check_sign(5)
assert result == -1, "Expected negative result"
