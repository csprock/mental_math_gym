import random

from base_classes import Problem
from base_classes import ProblemSetBaseClass


class TimesTables(ProblemSetBaseClass):

    prompt = "{0} x {1} = "

    def __init__(self, single_digits=False, exclude_tens_and_elevens=True):
        super().__init__(single_digits=single_digits, exclude_tens_and_elevens=exclude_tens_and_elevens)

    def new_problem(self):

        b = 12
        if self.single_digits:
            b = 9

        number_set = set(range(2,b))

        if self.exclude_tens_and_elevens:
            number_set = number_set - {10, 11}

        number_set = list(number_set)
        x = random.choice(number_set)
        y = random.choice(number_set)

        ans = x*y
        

        return Problem(ans, [x, y], self.prompt.format(*[x,y]))



class AdditionTables(ProblemSetBaseClass):

    prompt = "{0} + {1} = "

    def __init__(self, single_digits=True):
        super().__init__()
        self.single_digits = single_digits

    def new_problem(self):

        if self.single_digits:
            n = random.randint(2,9)
            m = random.randint(2,9)
        else:
            n = random.randint(2,99)
            m = random.randint(2,99)

        numbers = [m, n]
        ans = sum(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class SubtractionTables(ProblemSetBaseClass):

    prompt = "{0} - {1} = "

    def __init__(self, single_digits=True):
        super().__init__()
        self.single_digits = single_digits

    def new_problem(self):

        if self.single_digits:
            n = random.randint(3,9)
            m = random.randint(1, n-1)
        else:
            n = random.randint(3,99)
            m = random.randint(1, n-1)
        
        numbers = [n, m]
        ans = n - m

        return Problem(ans, numbers, self.prompt.format(*numbers))



LESSONS = {
    "Times Tables": TimesTables
}
