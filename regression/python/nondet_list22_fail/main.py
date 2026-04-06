def test_nondet_list_distinct_elements() -> None:
    """Test that nondet_list elements can be distinct (fail case)."""
    lst = nondet_list(3)
    __ESBMC_assume(len(lst) >= 2)
    assert lst[0] == lst[1]

test_nondet_list_distinct_elements()
