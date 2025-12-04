def div1(cond: int, x: int) -> int:
    """Example function with division by zero bug."""
    if not cond:
        return 42 // x
    else:
        return x // 10

# Test with specific values that trigger the bug
cond = 0
x = 0
result = div1(cond, x)
