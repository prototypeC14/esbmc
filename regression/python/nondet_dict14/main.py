def test_nondet_dict_str_keys() -> None:
       x = nondet_dict(2, key_type=str, value_type=int)
       __ESBMC_assume(len(x) > 0)
       k: str = nondet_str()
       if k in x:
           v = x[k]
           assert v == v

test_nondet_dict_str_keys()
