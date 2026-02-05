def count_entries(d):
    count = 0
    for key in d:
        count = count + 1
    if count > 1:
        return True
    return False

count_entries(nondet_dict(2))
