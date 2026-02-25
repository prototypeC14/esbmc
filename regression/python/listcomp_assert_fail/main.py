def test_list_comprehension():
    squares = [x * x for x in range(4)]
    assert squares == [0, 1, 4, 8]

test_list_comprehension()
