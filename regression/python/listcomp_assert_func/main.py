def double(x: int) -> int:
    return x * 2

nums = [1, 2, 3]
assert [double(x) for x in nums] == [2, 4, 6]
