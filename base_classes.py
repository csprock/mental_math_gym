import os
import time
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


def run_problemset(problem_set, clear_term=True):

    n_correct = 0
    missed = list()
    missed_problems = list()

    start = time.time()
    for problem in problem_set:

        prompt = problem.prompt
        print(prompt)
        user_answer = float(input())

        if user_answer == problem.answer:
            n_correct += 1
        else:
            missed.append((prompt + str(problem.answer), user_answer))
            missed_problems.append(problem)
        
        if clear_term:
            clear()
    end = time.time()

    problems_per_second = (end - start) / len(problem_set)

    return n_correct / len(problem_set), {"responses": missed, "problems": missed_problems}, problems_per_second

        

class InteractiveSession:

    def __init__(self, problem_set, clear_term=True, retry=False):
        self.problem_set = problem_set
        self.clear_term = clear_term
        self.retry = retry

    def __call__(self):
        if not self.problem_set:
            raise ValueError("Session has not been initialized with a problem")

        score_0, missed_0, problems_per_second_0 = run_problemset(self.problem_set)
        missed_problems = missed_0['problems']
        missed_responses = missed_0['responses']

        if self.retry:
            while len(missed_problems) > 0:
                print("missed the following: ")
                print(missed_responses)
                score_1, missed_1, problems_per_second_1 = run_problemset(missed_problems)
                missed_problems = missed_1['problems']
                missed_responses = missed_1['responses']
                
        
        if not self.retry:
            return score_0, missed_0['responses'], problems_per_second_0
        else:
            print("Initial score")
            return score_0, problems_per_second_0
    
