def test_nondet_dict_float_values() -> None:
    """Test nondet dictionary with float values."""
    x = nondet_dict(2, key_type=nondet_int(), value_type=nondet_float())
    __ESBMC_assume(len(x) > 0)
    
    # Test value access with nondet key
    k: int = nondet_int()
    if k in x:
        v = x[k]
        # v == v is not safe for floats (NaN != NaN per IEEE 754).
        # Just verify value access succeeds.
        assert isinstance(v, float)
test_nondet_dict_float_values()
