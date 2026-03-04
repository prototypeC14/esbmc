nums: list = [0, 1, 2, 3]

# Generator expression inside any()
assert any(x > 2 for x in nums)
assert not any(x > 10 for x in nums)

# With filtering condition
assert any(x == 3 for x in nums if x > 0)
assert not any(x == 5 for x in nums if x > 0)
