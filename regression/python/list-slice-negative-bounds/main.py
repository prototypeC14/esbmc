lst = [10, 20, 30, 40, 50]

# Negative lower, negative upper: lst[-3:-1] == [30, 40]
a = lst[-3:-1]
assert a[0] == 30
assert a[1] == 40

# Negative lower only: lst[-2:] should give last two elements [40, 50]
b = lst[-2:]
assert b[0] == 40
assert b[1] == 50
