def test_nondet_dict_multi_element() -> None:
    """Test that nondet_dict can generate dicts with multiple entries."""
    d = nondet_dict(3)
    assert len(d) < 4

test_nondet_dict_multi_element()
