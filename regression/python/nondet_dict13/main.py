def test_nondet_dict_access_value() -> None:
       x = nondet_dict(3, key_type=int, value_type=int)
       __ESBMC_assume(len(x) > 0)
       k: int = nondet_int()
       if k in x:
           v = x[k]
           assert v == v

test_nondet_dict_access_value()
