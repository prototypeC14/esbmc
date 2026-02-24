from typing import Any

def test_int_false(flag: bool) -> None:
    if flag:
        x: Any = 1
    else:
        x: Any = False
    y: Any = x

def test_int_true(flag: bool) -> None:
    if flag:
        x: Any = 1
    else:
        x: Any = True
    y: Any = x

def test_bool_float(flag: bool) -> None:
    if flag:
        x: Any = True
    else:
        x: Any = 1.5
    y: Any = x

test_int_false(True)
test_int_true(False)
test_bool_float(True)
