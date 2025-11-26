def validate_positive(n: int) -> int:
    assert n > 0, "n must be positive"
    return n * 2

# Call with valid input
validate_positive(5)
