def complex_check(x: int, y: int, z: int) -> int:
    if (x > 0 or y > 0) and z > 0:
        return 1
    else:
        return 0

# Cover all decision outcomes
complex_check(5, 3, 2)    # (T or T) and T = T
complex_check(5, 3, -1)   # (T or T) and F = F
complex_check(-1, -2, 2)  # (F or F) and T = F
complex_check(-1, -2, -1) # (F or F) and F = F
complex_check(5, -1, 2)   # (T or F) and T = T
complex_check(-1, 5, 2)   # (F or T) and T = T
