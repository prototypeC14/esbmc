def is_positive(n: int) -> int:
    if n > 0:
        return 1
    else:
        return 0

# Only cover positive branch
is_positive(10)
