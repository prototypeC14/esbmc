lst = [0, 1, 2, 3, 4]

# Out-of-bounds negative lower should clamp to 0
result = lst[-10:2]
assert result[0] == 0
assert result[1] == 1
