# This file contains the basic lessons, such as times tables, addition tables, and subtraction tables.

import random

from mathgen.common.problems import Problem
from mathgen.common.problems import ProblemSetBaseClass
from mathgen.common.registry import LessonParam, register_lesson


@register_lesson(
    id="basic.times_tables",
    title="Times Tables",
    description="Multiplication drill over 2..12 (optionally 2..9, and excluding 10 and 11).",
    unit="Basic",
    params=(
        LessonParam("single_digits", "bool", False, "Restrict factors to 2..9."),
        LessonParam(
            "exclude_tens_and_elevens",
            "bool",
            True,
            "Exclude 10 and 11 as factors.",
        ),
    ),
)
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



@register_lesson(
    id="basic.addition_tables",
    title="Addition Tables",
    description="Addition drill with single- or two-digit addends.",
    unit="Basic",
    params=(
        LessonParam("single_digits", "bool", True, "Restrict addends to 2..9."),
    ),
)
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


@register_lesson(
    id="basic.subtraction_tables",
    title="Subtraction Tables",
    description="Subtraction drill with positive results.",
    unit="Basic",
    params=(
        LessonParam("single_digits", "bool", True, "Restrict operands to 3..9."),
    ),
)
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