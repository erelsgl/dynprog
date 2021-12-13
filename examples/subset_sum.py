#!python3
"""
Uses the sequential dynamic programming function to solve the subset-sum problem.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog
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
    return dynprog.sequential.max_value(
        inputs = inputs,
        initial_states = _initial_states,
        transition_functions = _transition_functions,
        value_function = _value_function,
        filter_functions = _filter_functions(capacity)
    )


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
    return dynprog.sequential.max_value_solution(
        inputs = inputs,
        initial_states = _initial_states,
        transition_functions = _transition_functions,
        value_function = _value_function,
		initial_solution=_initial_solution,
		construction_functions = _construction_functions,
        filter_functions = _filter_functions(capacity)
    )[2]



# Common definitions:

_initial_states = [0]

_initial_solution = []

_transition_functions = [
	lambda state,input: state+input,    # adding the input
	lambda state,input: state+0,        # not adding the input
]

_construction_functions = [
	lambda solution,input: solution+[input],    # adding the input
	lambda solution,_:     solution,            # not adding the input
]

_value_function = lambda state: state

def _filter_functions(capacity:int):
	return [
            lambda state,input: state+input<=capacity,    # adding the input
            lambda _,__:        True,                     # not adding the input
        ]




if __name__=="__main__":
    import sys, logging
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    # dynprog.logger.setLevel(logging.INFO)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

