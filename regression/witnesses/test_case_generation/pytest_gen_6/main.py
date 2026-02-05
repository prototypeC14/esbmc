def sum_of_positive_elements(x):
    total = 0
    for item in x:
        if item > 0:
            total = total + item
    return total

sum_of_positive_elements(nondet_list(2))
