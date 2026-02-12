def test_nondet_dict_iteration() -> None:
    """Test iterating over nondet dictionary keys."""
    x = nondet_dict(3, key_type=int, value_type=int)
    __ESBMC_assume(len(x) == 2)
    
    count: int = 0
    for key in x:
        count = count + 1
        assert key in x
    
    assert count == 2
test_nondet_dict_iteration()
