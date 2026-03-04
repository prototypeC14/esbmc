class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

people: list = [
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Charlie", 22)
]

# any() with generator expression over objects
assert any(p.name == "Alice" for p in people), "Alice is missing!"
assert not any(p.name == "Dave" for p in people)

# any() with generator expression over simple list
nums: list = [0, 1, 2, 3]
assert any(x > 2 for x in nums)
assert not any(x > 10 for x in nums)

# any() with filtering condition
assert any(x == 3 for x in nums if x > 0)

# all() with generator expression
assert all(p.age > 0 for p in people)
assert not all(p.age > 25 for p in people)
