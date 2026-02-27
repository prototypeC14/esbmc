original = [[1, 2], [3, 4]]
shallow = original.copy()
original[0][0] = 99
assert shallow[0][0] == 99
