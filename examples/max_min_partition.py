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

import dynprog, math
from typing import *


def max_min_value(items:list, num_of_parts:int):
    """
    Returns the max-min value - does *not* return the partition itself.

    >>> max_min_value([1,2,3,4], 2)
    5
    >>> max_min_value([1,2,3,4,5], 2)
    7
    >>> max_min_value([11,22,33,44,55,66,77,88,99], 3)
    165
    """
    # Algorithm: add the numbers one by one to all possible bundles.
    num_of_items = len(items)
    def initial_states():  # returns (state,value) tuples
        zero_values = num_of_parts*(0,)
        yield ( (0, zero_values), -math.inf)
    def neighbors (state:Tuple[int,tuple], value:int):   # returns (state,value) tuples
        (item_index, values) = state
        if item_index < num_of_items:
            item = items[item_index]
            next_index = item_index+1
            for j in range(num_of_parts):
                new_values = list(values)
                new_values[j] += item
                state_value = -math.inf if next_index < num_of_items else min(new_values)
                yield ((next_index, tuple(sorted(new_values))), state_value)
    def is_final_state(state):
        return state[0]==num_of_items
    return dynprog.max_value(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)

def max_min_partition(items:list, num_of_parts:int):
    """
    Returns the max-min partition.

    >>> max_min_partition([1,2,3,4], 2)
    (5, [[1, 4], [2, 3]])
    >>> max_min_partition([1,2,3,4,5], 2)
    (7, [[1, 2, 4], [3, 5]])
    >>> max_min_partition([11,22,33,44,55,66,77,88,99], 3)
    (165, [[11, 22, 33, 44, 55], [66, 99], [77, 88]])
    """
    # Algorithm: add the numbers one by one to all possible bundles.
    num_of_items = len(items)
    def initial_states():  # returns (state,value,data) tuples
        zero_values = num_of_parts*(0,)
        empty_partition = num_of_parts*([],)
        yield ( (0, zero_values), -math.inf, empty_partition)
    def neighbors (state:Tuple[int,tuple], value:int, partition:list):   # returns (state,value,data) tuples
        (item_index, part_values) = state
        if item_index < num_of_items:
            item = items[item_index]
            next_index = item_index+1
            for j in range(num_of_parts):
                new_part_values = list(part_values)
                new_part_values[j] += item
                # if sorted(new_part_values)!=new_part_values:
                #     continue    # keep only sorted states, to reduce redundancies.
                state_value = -math.inf if next_index < num_of_items else min(new_part_values)
                new_partition = list(partition)
                new_partition[j] = new_partition[j] + [item]
                yield ((next_index, tuple(new_part_values)), state_value, new_partition)
    def is_final_state(state):
        return state[0]==num_of_items
    (state, value, data, num_of_states) = dynprog.max_value_solution(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
    return (value,data)


if __name__=="__main__":
    import sys, logging
    dynprog.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.logger.setLevel(logging.WARNING)
    print(max_min_value(5*[11]+5*[23], 2))
    print(max_min_partition(5*[11]+5*[23], 2))
