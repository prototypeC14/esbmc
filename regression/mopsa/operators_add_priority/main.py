class X:
    def __add__(self, other):
        return 10

class Y:
    def __radd__(self, other):
        return 20

# X has __add__, so it should be used (not Y.__radd__)
res = X() + Y()
assert res == 10
