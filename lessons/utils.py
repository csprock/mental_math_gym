import random


def subtraction_same_magnitude(d=0):

    start = 10 ** d + 1
    end = 10**(d+1) - 1

    n1 = random.randint(start, end)
    n2 = random.randint(start, max(n1-1, start))

    return n1, n2


def subtraction_different_magnitude(d, diff):
    d2 = d - diff
    assert d2 > 0

    start = 10 ** d + 1
    end = 10**(d+1) - 1

    n1 = random.randint(start, end)

    if d == 1:
        n2 = random.randint(2, 9)
    else:
        start = 10 ** d2 + 1
        end = 10**(d2+1) - 1

        n2 = random.randint(start, end)

    return n1, n2
