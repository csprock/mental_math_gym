import os
from collections import namedtuple

def clear():
    os.system('clear')


Problem = namedtuple("Problem", ["answer", "inputs", "prompt"])


class ProblemSetBaseClass:

    def __init__(self, **kwargs):

        for k, v in kwargs.items():
            setattr(self, k, v)

    def new_problem(self):
        raise NotImplemented
    
    def problem_set(self, n):

        problems = list()
        for i in range(0, n):
            problems.append(self.new_problem())

        return problems

        

class InteractiveSession:

    def __init__(self, problem_set):
        self.problem_set

    def __call__(self):
        if not self.problem_set:
            raise ValueError("Session has not been initialized with a problem")
        
        n_correct = 0
        missed = list()

        for problem in self.problems:

            prompt = problem.prompt
            print(prompt)
            user_answer = float(input())

            if user_answer == problem.answer:
                n_correct += 1
            else:
                missed.append((prompt, user_answer))
            
            if self.clear:
                clear()

        return n_correct, self.n, missed
    
