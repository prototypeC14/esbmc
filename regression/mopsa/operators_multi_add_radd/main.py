# Test: multiple classes with __add__ (attribute access) followed by multiple __radd__ calls
# Stress test: two different classes with attribute-accessing __add__,
# then multiple cross-type __radd__ calls to detect state corruption
class D1:
    def __init__(self):
        self.v = 1

    def __add__(self, other):
        return self.v + other.v

class D2:
    def __init__(self):
        self.w = 5

    def __add__(self, other):
        return self.w + other.w

# Execute both __add__ methods to pollute symbol table state
_ = D1() + D1()
_ = D2() + D2()

class E:
    pass

class F:
    def __radd__(self, other):
        return 77

class G:
    def __radd__(self, other):
        return 88

# Multiple cross-type __radd__ calls after attribute-accessing __add__
res1 = E() + F()
assert res1 == 77

res2 = E() + G()
assert res2 == 88
