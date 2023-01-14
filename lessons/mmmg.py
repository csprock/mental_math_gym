# """ Problems from 'Mental Math in the Middle Grades' """

import random

from base_classes import Problem
from base_classes import ProblemSetBaseClass
from lessons.utils import * 

### Unit 1 Problems ###

class Lesson1(ProblemSetBaseClass):

    """ One Step at a Time
    
    Adding multiples of powers of ten
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

    """ Using Place Values Names
    
    Adding multiples of power of ten
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
    
    """ Break it Up #1

    Adding by expanding the second addened
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
    
    """ Break it Up #2
    
    Adding by expanding the second addend
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
    """ Dropping common zeros

    Subtracting multiples of powers of ten
    """

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
    """ Dropping common zeros 
    
    Subtracting multiples of ten
    """
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
    """ Front-end Focus 
    
    Subtracting numbers ending in the same digits
    """
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
    """ Starting at the left 
    
    Adding from the front end (when regrouping is needed)
    """
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
    """ Starting at the left 
    
    Subtracting from the front end (when no regrouping is needed)
    """
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
    """ Working with Fives 
    
    
    Adding by expanding to numbers ending in 5
    """

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


class Lesson13(ProblemSetBaseClass):
    """ Trading off
    
    Adding by making multiples of ten then adjusting
    """

    prompt = "{0} + {1}"

    def __init__(self):
        super().__init__()


    def new_problem(self):

        b = random.randint(2, 9) * 10
        d = random.randint(7,9)
        n = b + d
        m = random.randint(11, 99)

        numbers = [n, m]
        ans = n + m

        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson14(ProblemSetBaseClass):
    """ Balancing Subtraction
    
    Subtracting by making multiples of ten and adjusting
    """


    prompt = "{0} - {1}"

    def __init__(self):
        super().__init__()


    def new_problem(self):

        b = random.randint(2, 9) * 10
        d = random.randint(7, 9)
        n = b + d
        m = random.randint(n+1, 999)
        
        numbers = [m, n]
        ans = m - n

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson15(ProblemSetBaseClass):
    """ Searching for Compatibles 
    
    Identifying pairs that sum to 100 and 1000
    """

    prompt_add = "{0} + {1}"
    prompt_sub = "{0} - {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):

        if random.random() < 0.5:
            b = random.randint(2, 9) * 10
            d = random.randint(7,9)
            n = b + d
            m = random.randint(11, 99)

            numbers = [n, m]
            if random.random() < 0.5:
                numbers = [i*10 for i in numbers]
            ans = sum(numbers)

            random.shuffle(numbers)

            return Problem(ans, numbers, self.prompt_add.format(*numbers))

        else:
            n = random.choice([100, 1000])
            m = random.randint(11, 99)
            if n / 10 == 100:
                m = m*10
            
            numbers = [n, m]
            ans = n - m

            return Problem(ans, numbers, self.prompt_sub.format(*numbers))


class Lesson16(ProblemSetBaseClass):
    """ Searching for Compatibles

    Identifying compatibles numbers for various multiples of ten
    """

    prompt_add = "{0} + {1}"
    prompt_sub = "{0} - {1}"

    def __init__(self):
        super().__init__()

    # TODO: add non-compatible subtraction and addition
    def new_problem(self):
        
        if random.random() < 0.5:
            s = random.randint(1, 9) * 10
            n = random.randint(1, s-1)
            m = s - n

            if random.random():
                n = n * 10
                m = m * 10
            
            numbers = [n, m]
            random.shuffle(numbers)
            ans = sum(numbers)

            return Problem(ans, numbers, self.prompt_add.format(*numbers))

        else:
            s = random.randint(1, 9) * 10
            n = random.randint(1, 99)
            m = s + n

            if random.random() < 0.5:
                n = n * 10
                m = m * 10

            numbers = [m, n]
            ans = m - n

            return Problem(ans, numbers, self.prompt_sub.format(*numbers))


class Lesson18(ProblemSetBaseClass):

    """
    Make your own compatibles

    """

    prompt = "{0} + {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):

        if random.random() < 0.5:
            m = random.randint(10, 200-1) * 5
        else:
            m = random.randint(10, 99) * 10

        n = random.randint(11, 99)

        numbers = [n, m]
        ans = sum(numbers)
        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson19(ProblemSetBaseClass):
    """
    Adding multiples of 25
    """

    prompt = "{0} + {1} + {2}"

    def __init__(self):
        super().__init__()

    def new_problem(self):

        multiples_of_25 = [25*i for i in [1,2,3,4,5,6,7]]
        numbers = random.choices(multiples_of_25, k=3)

        ans = sum(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson20(ProblemSetBaseClass):
    """
    Using compensation when adding numbers ending in 8 and 9
    """

    prompt = "{0} + {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):
        b = random.choice([8,9,98,99])
        if b / 10 < 1:
            n = random.randint(1, 9) * 10 + b
            m = random.randint(11, 99) if random.random() < 0.5 else random.randint(101, 997)
        else:
            n = random.randint(1, 9) * 100 + b
            m = random.randint(101, 997) if random.random() < 0.5 else random.randint(1001, 9997)

        numbers = [n, m]
        ans = sum(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))



class Lesson21(ProblemSetBaseClass):
    """
    Using compensation when subtracting numbers ending in 8 and 9
    """

    prompt = "{0} - {1}"

    def __init__(self):
        super().__init__()

    
    def new_problem(self):
        b = random.choice([8,9,98,99])
        if b / 10 < 1:
            n = random.randint(1, 9)*10 + b
            m = random.randint(n+1, 999)
        else:
            n = random.randint(1, 9)*100 + b
            m = random.randint(n+1,9999)
        
        ans = m - n
        numbers = [m, n]

        return Problem(ans, numbers, self.prompt.format(*numbers))



class Lesson22(ProblemSetBaseClass):
    """
    Multiplying by powers of ten
    """

    prompt = "{0} x {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):
        n = 10**random.randint(1,3)
        m = random.randint(2,999)
        ans = m * n
        numbers = [n,m]

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson23(ProblemSetBaseClass):
    """
    Multiplying where there are trailing zeros in one factor
    """

    prompt = "{0} x {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):
        p = random.randint(1,3)
        n = random.randint(1,9)*10**p

        if random.random() < 0.5:
            m = random.randint(1,9)
        else:
            n = random.randint(2,99)
        
        ans = n * m
        numbers = [n, m]
        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson24(ProblemSetBaseClass):
    """
    multiplying when there are trailing zeros in two factors
    """

    prompt = "{0} x {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):
        n = rrandom.randint(1,9)*10**random.randint(1,3)
        m = random.randint(1,9)*10**random.randint(1,3)

        ans = m * n
        numbers = [m, n]
        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson25(ProblemSetBaseClass):
    """
    multiplying by expanding a two-digit factor
    """

    prompt = "{0} x {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):
        n = random.randint(11,99)
        m = random.randint(2,9)
        ans = n * m
        numbers = [n, m]
        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson26(ProblemSetBaseClass):
    """
    multiplying by expanding a three-digit factor
    """
    prompt = "{0} x {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):
        n = random.randint(2,9)
        if random.random() < 0.5:
            m = random.randint(11,99)*10 + random.choice([0, 5])
        else:
            m = random.randint(101, 999)
        
        ans = m * n
        numbers = [m, n]
        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))


class Lesson27(ProblemSetBaseClass):
    """
    multiplying when one factor ends in nine
    """
    prompt = "{0} x {1}"

    def __init__(self):
        super().__init__()

    def new_problem(self):
        n = random.randint(2,9)
        m = random.randint(0,9)*100 + 99
        if random.random() < 0.5:
            m /= 100
        
        ans = round(m * n, 2) # edge-cases
        numbers = [m, n]
        random.shuffle(numbers)

        return Problem(ans, numbers, self.prompt.format(*numbers))

