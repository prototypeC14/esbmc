def check_range(x: int, y: int) -> int:
    if x > 0 and y > 0:
        return 1
    else:
        return 0

# Cover all decision outcomes: TT, TF, FT, FF
check_range(5, 3)   # T and T = T
check_range(5, -1)  # T and F = F
check_range(-1, 3)  # F and T = F
check_range(-1, -1) # F and F = F
