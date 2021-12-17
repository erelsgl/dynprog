#!python3
"""
Uses the sequential dynamic programming function to solve the knapsack problem.

Each input contains two integers: the weight and the value.
The state contains two integers: the total weight and the total value.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog
from dynprog.sequential import SequentialDynamicProgram

from typing import *



def max_value(weights: List[int], values: List[int], capacity:int)->int:
    """
    Returns the maximum sum of values from the given `inputs` list, that can fit within a bin of the given 'capacity'.

    >>> max_value([3,5], [10,20], 2)
    0
    >>> max_value([3,5], [10,20], 4)
    10
    >>> max_value([3,5], [20,10], 4)
    20
    >>> max_value([3,5], [10,20], 6)
    20
    >>> max_value([3,5], [20,10], 6)
    20
    >>> max_value([3,5], [10,20], 8)
    30
    """
    return KnapsackDP(capacity).max_value(inputs=zip(weights,values))


def max_value_solution(weights: List[int], values: List[int], capacity:int)->int:
    """
    Returns the maximum sum of values from the given `inputs` list, that can fit within a bin of the given 'capacity'.

    >>> max_value_solution([3,5], [10,10], 2)
    []
    >>> max_value_solution([3,5], [10,20], 4)
    [3]
    >>> max_value_solution([3,5], [20,10], 4)
    [3]
    >>> max_value_solution([3,5], [10,20], 6)
    [5]
    >>> max_value_solution([3,5], [20,10], 6)
    [5]
    >>> max_value_solution([3,5], [10,20], 8)
    [3, 5]
    """
    return KnapsackDP(capacity).max_value_solution(inputs=zip(weights,values))[2]





#### Dynamic program definition:

class KnapsackDP(SequentialDynamicProgram):

    # The state contains two numbers: (weight,value).

    def __init__(self, capacity:int):
        self.capacity = capacity

    def initial_states(self):
        return [(0,0)]

    def initial_solution(self):
        return []

    def transition_functions(self):
        return  [
            lambda state,input: (state[0]+input[0], state[1]+input[1]),    # adding the input
            lambda state,input: state,                                     # not adding the input
        ]

    def construction_functions(self):
        return  [
            lambda solution,input: solution+[input],    # adding the input
            lambda solution,_:     solution,            # not adding the input
        ]

    def value_function(self):
        return lambda state: state[1]  # the state is: (weight,value)

    def filter_functions(self):
        return [
            lambda state,input: state[0]+input[0]<=self.capacity,    # adding the input: (weight,value)
            lambda _,__:        True,                                # not adding the input
        ]




if __name__=="__main__":
    import sys, logging
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.sequential.logger.setLevel(logging.INFO)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

