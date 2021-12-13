#!python3

"""
Uses the generic dynamic programming function to solve the
max-min number partitioning problem.

The states are of the form  (i, (v1, v2, ..., vk)) where k is the number of parts.
The "i" is the number of items allocated so far.
The "v1,...,vk" are the values of the bundles.

Programmer: Erel Segal-Halevi
Since: 2021-11
"""

import dynprog
from typing import *


def _initial_states(num_of_parts:int):
    zero_values = num_of_parts*(0,)
    return [zero_values]

def _initial_solution(num_of_parts:int):
    empty_bundles = [ [] for _ in range(num_of_parts)]
    return empty_bundles


   
def _add_input_to_part_sum(part_sums:list, part_index:int, input:int):
    """
    Adds the given input integer to part #part_index in the given list of parts.
    >>> _add_input_to_part_sum([11, 22, 33], 0, 77)
    [88, 22, 33]
    >>> _add_input_to_part_sum([11, 22, 33], 1, 77)
    [11, 99, 33]
    >>> _add_input_to_part_sum([11, 22, 33], 2, 77)
    [11, 22, 110]
    """
    new_part_sums = list(part_sums)
    new_part_sums[part_index] = new_part_sums[part_index] + input
    return new_part_sums
def _transition_functions(num_of_parts:int):
    """
    >>> for f in _transition_functions(3): f([11,22,33],77)
    [88, 22, 33]
    [11, 99, 33]
    [11, 22, 110]
    """
    return [
        lambda state, input, part_index=part_index: _add_input_to_part_sum(state, part_index, input)
        for part_index in range(num_of_parts)
    ]


def _add_input_to_part(parts:list, part_index:int, input:int):
    """
    Adds the given input integer to part #part_index in the given list of parts.
    >>> _add_input_to_part([[11,22], [33,44], [55,66]], 1, 77)
    [[11, 22], [33, 44, 77], [55, 66]]
    """
    new_parts = list(parts)
    new_parts[part_index] = new_parts[part_index]+[input]
    return new_parts
def _construction_functions(num_of_parts:int):
    return [
        lambda solution,input,part_index=part_index: _add_input_to_part(solution, part_index, input)
        for part_index in range(num_of_parts)
    ]


_value_function = lambda state: min(state)




def max_min_value(items:List[int], num_of_parts:int):
    """
    Returns the max-min value - does *not* return the partition itself.

    >>> max_min_value([1,2,3,4], 2)
    5
    >>> max_min_value([1,2,3,4,5], 2)
    7
    >>> max_min_value([11,22,33,44,55,66,77,88,99], 3)
    165
    """
    return dynprog.sequential.max_value(
        inputs = items,
        initial_states = _initial_states(num_of_parts),
        transition_functions = _transition_functions(num_of_parts),
        value_function = _value_function,
        filter_functions = None
    )

def max_min_partition(items:list, num_of_parts:int):
    """
    Returns the max-min partition.

    >>> max_min_partition([1,2,3,4], 2)
    (5, [[1, 4], [2, 3]])
    >>> max_min_partition([1,2,3,4,5], 2)
    (7, [[3, 5], [1, 2, 4]])
    >>> max_min_partition([11,22,33,44,55,66,77,88,99], 3)
    (165, [[66, 99], [77, 88], [11, 22, 33, 44, 55]])
    """
    return dynprog.sequential.max_value_solution(
        inputs = items,
        initial_states = _initial_states(num_of_parts),
        transition_functions = _transition_functions(num_of_parts),
        value_function = _value_function,
		initial_solution=_initial_solution(num_of_parts),
		construction_functions = _construction_functions(num_of_parts),
        filter_functions = None
    )[1:3]


if __name__=="__main__":
    import sys, logging
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.sequential.logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.sequential.logger.setLevel(logging.WARNING)
    print(max_min_value(5*[11]+5*[23], 2))
    print(max_min_partition(5*[11]+5*[23], 2))
