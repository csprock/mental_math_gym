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




LESSONS = {
    "Times Tables": TimesTables
}