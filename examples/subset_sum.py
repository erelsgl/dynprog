#!python3
"""
Uses the sequential dynamic programming function to solve the subset-sum problem.

The state contains a single number: the current sum.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog
from dynprog.sequential import SequentialDynamicProgram

from typing import *



def max_value(inputs: List[int], capacity:int)->int:
    """
    Returns the maximum sum of values from the given `inputs` list, that can fit within a bin of the given 'capacity'.

    >>> max_value([3,5], 2)
    0
    >>> max_value([3,5], 4)
    3
    >>> max_value([3,5], 6)
    5
    >>> max_value([3,5], 8)
    8
    >>> max_value([100,200,400,700,1100,1600,2200,2900,3700], 4005)
    4000
    """
    return SubsetSumDP(capacity).max_value(inputs)


def max_value_solution(inputs: List[int], capacity:int)->int:
    """
    Returns the maximum sum of values from the given `inputs` list, that can fit within a bin of the given 'capacity'.

    >>> max_value_solution([3,5], 2)
    []
    >>> max_value_solution([3,5], 4)
    [3]
    >>> max_value_solution([3,5], 6)
    [5]
    >>> max_value_solution([3,5], 8)
    [3, 5]
    >>> max_value_solution([100,200,400,700,1100,1600,2200,2900,3700], 4005)
    [100, 200, 3700]
    """
    return SubsetSumDP(capacity).max_value_solution(inputs)[2]





#### Dynamic program definition:

class SubsetSumDP(SequentialDynamicProgram):

    # The state contains a single number: the current sum.

    def __init__(self, capacity:int):
        self.capacity = capacity

    def initial_states(self):
        return [0]

    def initial_solution(self):
        return []

    def transition_functions(self):
        return  [
            lambda state,input: state+input,    # adding the input
            lambda state,input: state+0,        # not adding the input
        ]

    def construction_functions(self):
        return  [
            lambda solution,input: solution+[input],    # adding the input
            lambda solution,_:     solution,            # not adding the input
        ]

    def value_function(self):
        return lambda state: state

    def filter_functions(self):
        return [
            lambda state,input: state+input<=self.capacity,    # adding the input
            lambda _,__:        True,                     # not adding the input
        ]




if __name__=="__main__":
    import sys, logging
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    # dynprog.logger.setLevel(logging.INFO)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

