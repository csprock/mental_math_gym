# """ Problems from 'Mental Math in the Middle Grades' """

import random

from base_classes import Problem
from base_classes import ProblemSetBaseClass
from lessons.utils import * 

### Unit 1 Problems ###

class Lesson1(ProblemSetBaseClass):

    """ One Step at a Time
    
    Skill: add multiples of powers of ten
    """

    prompt = "{0} + {1} + {2} = "
    def __init__(self):
        super().__init__()


    def new_problem(self):
        
        x_set = [x for x in range(10, 100, 10)]
        y_set = [y for y in range(100, 1000, 100)]
        z_set = y_set
        if random.random() < 0.5:
            z_set = [z for z in range(1000, 10000, 1000)]

        x = random.choice(x_set)
        y = random.choice(y_set)
        z = random.choice(z_set)

        ans = x + y + z

        return Problem(ans, [z, y, x], self.prompt.format(*[z, y, x]))
        
    
class Lesson2(ProblemSetBaseClass):

    """ Using Place Values
    

    """
    prompt = "{0} + {1} = "


    def __init__(self):
        super().__init__()

    def new_problem(self):

        if random.random() < 0.5:
            x = random.choice([x for x in range(10, 1000, 10)]) 
            y = random.choice([y for y in range(100, 1000, 100)])
        else:
            x = random.choice([x for x in range(100, 10000, 100)]) 
            y = random.choice([y for y in range(100, 1000, 10)])

        ans = x + y

        if random.random() < 0.5:
            numbers = [x,y]
        else:
            numbers = [y,x]

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson3(ProblemSetBaseClass):

    pass

class Lesson4(ProblemSetBaseClass):
    
    """ Break it Up 1
    
    """
    prompt = "{0} + {1} + {2} = "

    def __init__(self):
        super().__init__()


    def new_problem(self):

        if random.random() < 0.5:
            z_max = 100
        else:
            z_max = 1000
        z = random.choice([x for x in range(11, z_max)])

        if random.random() < 0.5:
            y = random.choice([x for x in range(10, 100, 10)])
            x = random.choice([x for x in range(2, 10)])
        else:
            y = random.choice([x for x in range(100, 1000, 100)])
            x = random.choice([x for x in range(10, 100, 100)])

        numbers = [z, y, x]
        ans = sum(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))
        
    

class Lesson5(ProblemSetBaseClass):
    
    """ Break it Up 1
    
    """
    prompt = "{0} + {1} + {2} = "

    def __init__(self):
        super().__init__()


    def new_problem(self):

        z = random.choice([x for x in range(11, 100)])
        y = random.choice([x for x in range(10, 100, 100)])
        x = random.choice([x for x in range(2, 10)])

        numbers = [z, y, x]
        ans = sum(numbers)
        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson6(ProblemSetBaseClass):
    """ Dropping common zeros"""

    prompt1 = "{0} - {1}"
    prompt2 = "{0} - {1} - {2}"

    def __init__(self):
        super().__init__()

    def _two_numbers(self, same_power=False):

        if same_power:
            n1 = random.randint(3, 9)
            n2 = random.randint(2, n1-1)
            m = random.randint(2,3)

            return n1*(10**m), n2*(10**m)

        else:
            n1 = random.randint(2, 9)
            n2 = random.randint(2, 9)
            m1 = random.randint(2,3)
            m2 = random.randint(max(1, m1-2), m1-1)

            return n1*(10**m1), n2*(10**m2)

    def _three_numbers(self):

        n1, n2 = self._two_numbers()

        if min([n1, n2]) / 10 > 10:
            n3 = random.randint(2,9) * 10
        else:
            return self._three_numbers()

        return n1, n2, n3

    def new_problem(self):

        if random.random() < 0.5:
            n1, n2 = self._two_numbers()
            return Problem(n1 - n2, [n1, n2], self.prompt1)
        else:
            n1, n2, n3 = self._three_numbers()
            return Problem(n1 - n2 - n3, [n1, n2, n3], self.prompt2.format(*[n1, n2, n3]))


class Lesson7(ProblemSetBaseClass):
    """ Dropping common zeros """
    prompt = "{0} - {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):

        n1 = random.randint(11, 99) * (10 ** random.randint(1,2))
        n2 = random.randint(1,9) * (10 ** random.randint(1,2))

        if n2 >= n1:
            return self.new_problem()

        ans = n1 - n2
        return Problem(ans, [n1, n2], self.prompt.format(*[n1, n2]))


    
class Lesson8(ProblemSetBaseClass):
    """ Front-end Focus """
    prompt = "{0} - {1}"



    def __init__(self):
        super().__init__()

    def new_problem(self):
        last_digit = random.randint(1,99)

        if random.random() < 0.5:
            # same magnitude
            if last_digit // 10 == 0:
                n1, n2 = subtraction_same_magnitude(d=1)
            else:
                n1, n2 = subtraction_same_magnitude(d=0)
        else:
            n1, n2 = subtraction_different_magnitude(d=1, diff=0)


        n1 = int(str(n1) + str(last_digit))
        n2 = int(str(n2) + str(last_digit))

        ans = n1 - n2

        return Problem(ans, [n1, n2], self.prompt.format(*[n1, n2]))


#### unit 2 ####

class Lesson10(ProblemSetBaseClass):
    """ Starting at the left """
    prompt = "{0} + {1}"


    def __init__(self):
        super().__init__()

    def new_problem(self):

        d = random.randint(2,3)

        if d == 2:
            n1 = random.randint(11, 99)
            n2 = random.randint(11, 99)
        else:
            n1 = random.randint(101, 999)
            n2 = random.randint(101, 999)

        ans = n1 + n2

        return Problem(ans, [n1, n2], self.prompt.format(*[n1, n2]))


class Lesson11(ProblemSetBaseClass):
    """ Starting at the left """
    prompt = "{0} - {1}"


    def __init__(self):
        super().__init__()

    def new_problem(self):
        
        d = random.randint(2,3)

        arr1 = list()
        arr2 = list()

        for j in range(0, d):
            n1 = random.randint(2, 9)
            n2 = random.randint(1, n1 - 1)
            arr1.append(n1)
            arr2.append(n2)

        arr1 = int("".join([str(x) for x in arr1]))
        arr2 = int("".join([str(x) for x in arr2]))

        assert arr1 > arr2

        ans = arr1 - arr2

        return Problem(ans, [arr1, arr2], self.prompt.format(*[arr1, arr2]))


class Lesson12(ProblemSetBaseClass):
    """ Working with Fives """

    prompt = "{0} + {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):

        n1 = int(str(random.randint(1, 9)) + str(5))

        if random.random() < 0.5:
            n2 = random.randint(1, 9)
        else:
            n2 = random.randint(10, 99)

        ans = n1 + n2

        return Problem(ans, [n1, n2], self.prompt.format(*[n1, n2]))

