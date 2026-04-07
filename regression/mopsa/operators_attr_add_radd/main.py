# Test: __add__ with attribute access executed before cross-type __radd__
# This is the EXACT crash condition from the issue:
# 1. __add__ uses attribute access (self.x + other.x)
# 2. __add__ is actually executed (B() + B())
# 3. A subsequent expression requires __radd__ fallback across different types
class B:
    def __init__(self):
        self.x = 1

    def __add__(self, other):
        return self.x + other.x

# Execute __add__ with attribute access - this must happen first
_ = B() + B()

class A:
    pass

class C:
    def __radd__(self, other):
        return 0

# Cross-type operation requiring __radd__ fallback
res = A() + C()
assert res == 0
