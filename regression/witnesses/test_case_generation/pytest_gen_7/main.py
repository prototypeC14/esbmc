def sum_of_positive_elements(x):
    total = 0
    for key in x:
        if x[key] > 0:
            total = total + x[key]
    return total

sum_of_positive_elements(nondet_dict(2, key_type=nondet_int(), value_type=nondet_int()))
