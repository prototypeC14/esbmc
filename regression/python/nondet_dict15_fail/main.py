def test_nondet_dict_multi_element_fail() -> None:
    """Test that nondet_dict can generate dicts with 2+ entries (fail case)."""
    d = nondet_dict(3)
    assert len(d) < 2

test_nondet_dict_multi_element_fail()
