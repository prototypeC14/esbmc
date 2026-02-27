lst = [10, 20, 30, 40, 50]

# Out-of-bounds negative lower with negative upper: lst[-100:-2] == lst[0:-2] == [10, 20, 30]
a = lst[-100:-2]
assert a[0] == 10
assert a[1] == 20
assert a[2] == 30

# Regular positive slice (sanity check)
b = lst[1:4]
assert b[0] == 20
assert b[1] == 30
assert b[2] == 40
