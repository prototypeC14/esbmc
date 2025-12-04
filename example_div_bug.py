def div1(cond: int, x: int) -> int:
    """Example function with division by zero bug."""
    if not cond:
        return 42 // x
    else:
        return x // 10

if __name__ == "__main__":
    # Test with specific values that trigger the bug
    cond = 0
    x = 0
    result = div1(cond, x)
