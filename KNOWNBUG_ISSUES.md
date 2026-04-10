# Python Frontend KNOWNBUG Issues

## Issue 1: Closures and first-class functions not supported

**Test:** `regression/python/higher-order3`

**Reproducer:**
```python
def make_multiplier(k):
    def mul(x):
        return x * k
    return mul

times3 = make_multiplier(3)
times3(4)   # expected: 12
```

**Error:**
```
ERROR: Function `py:main.py@times3' type mismatch: expected code
ERROR: failed to find function `py:main.py@times3'
```

ESBMC does not support returning inner functions (closures). `times3` is not recognized as callable.

---

## Issue 2: Dynamic dispatch calls base class instead of overridden method

**Test:** `regression/python/polymorphism02`

**Reproducer:**
```python
class Vehicle:
    def move(self):
        raise NotImplementedError

class Car(Vehicle):
    def move(self):
        return "Driving on the road"

def test_vehicle_movement(vehicle, expected):
    result: str = vehicle.move()
    assert result == expected

test_vehicle_movement(Car(), "Driving on the road")
```

**Error:**
```
Throwing an exception of type NotImplementedError but there is not catch for it.
```

ESBMC dispatches to `Vehicle.move()` instead of `Car.move()`.

---

## Issue 3: Method chaining on returned object gives wrong type

**Test:** `regression/python/nested-attr-7`

**Reproducer:**
```python
class Node:
    def __init__(self, value: int) -> None:
        self.value: int = value
    def get_value(self) -> int:
        return self.value

class ListBuilder:
    def __init__(self) -> None:
        self.head: Node = Node(1)
    def build(self) -> Node:
        return self.head

class Manager:
    def __init__(self) -> None:
        self.builder: ListBuilder = ListBuilder()
    def get_head_value(self) -> int:
        result = self.builder.build().get_value()
        return result

manager = Manager()
assert manager.get_head_value() == 1
```

**Error:**
```
AttributeError: 'str' object has no attribute 'get_value'
```

`build()` returns `Node` but ESBMC infers it as `str`.

---

## Issue 4: List access fails with typed class attributes and method return values

**Test:** `regression/python/github_2012`

**Reproducer:**
```python
from typing import List

class JIRA:
    def __init__(self, server: str):
        self.issues: List[str] = []
    def search_issues(self, query: str) -> List[str]:
        return ["IKUT-123", "IKUT-456"]

jira = JIRA(server="https://example.com")
results = jira.search_issues("query")
for issue in results:
    print(issue)
```

**Error:**
```
ERROR: Invalid list access: could not resolve position or element type
```

---

## Issue 5: `reversed()` builtin causes infinite BMC unrolling

**Test:** `regression/python/reversed1`

**Reproducer:**
```python
import math

def minimumCoins_v6(prices: list[int]) -> int:
    n = len(prices)
    dp = [math.inf] * (n + 1)
    dp[-1] = 0
    for i in reversed(range(n)):
        dp[i] = prices[i] + min(dp[j] for j in range(i + 1, min(2 * i + 2, n) + 1))
    return dp[0]
```

**Error:** ESBMC hangs indefinitely after GOTO program creation.

---

## Issue 6: `os` module functions modeled incorrectly — always succeed

**Test:** `regression/python/import-os2_fail`

**Reproducer:**
```python
from os import remove

def delete_file(path: str) -> bool:
    try:
        remove(path)
        return True
    except FileNotFoundError:
        return False

result = delete_file("/tmp/testfile.txt")
assert result == True  # should be VERIFICATION FAILED
```

**Error:** Expects `VERIFICATION FAILED` but gets `VERIFICATION SUCCESSFUL`. `os.remove()` is modeled as always succeeding.

---

## Issue 7: Polymorphism + lambda + list comprehension combined failure

**Tests:** `regression/python/jpl`, `regression/python/jpl_1`

**Reproducer:**
```python
class Action:
    def pre(self) -> bool:
        raise NotImplementedError
    def act(self) -> None:
        raise NotImplementedError

class Down(Action):
    def pre(self) -> bool:
        return counter > 0
    def act(self) -> None:
        global counter
        counter -= 1

class Up(Action):
    def pre(self) -> bool:
        return counter < 1
    def act(self) -> None:
        global counter
        counter += 1

counter: int = 1
actions = [Down(), Up()]
enabled = [a for a in actions if a.pre()]
enabled[0].act()
```

**Error:**
```
dereference failure: Access to object out of bounds
```

Multiple features interact: dynamic dispatch, lambda, heterogeneous list. Root cause likely overlaps with Issue 2 (dynamic dispatch).
