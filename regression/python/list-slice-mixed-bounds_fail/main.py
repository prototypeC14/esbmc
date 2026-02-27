lst = [10, 20, 30, 40, 50]

# lst[-100:-2] clamps to lst[0:-2] == [10, 20, 30]
a = lst[-100:-2]
assert a[0] == 99  # wrong: should be 10
