lst = [10, 20, 30, 40, 50]

# lst[-3:-1] == [30, 40]
a = lst[-3:-1]
assert a[0] == 99  # wrong: should be 30
