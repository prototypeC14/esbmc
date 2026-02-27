lst = [0, 1, 2, 3, 4]

# Out-of-bounds negative lower clamps to 0, so lst[-10:2] == [0, 1]
result = lst[-10:2]
assert result[0] == 99  # wrong: should be 0
