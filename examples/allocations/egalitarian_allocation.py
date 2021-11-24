#!python3

"""
Uses the generic dynamic programming function to find an egalitarian (max-min)
allocation of items to agents with different valuations.

This is a generalization of max_min_partition.py.

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are of the form  (j, (v1, v2, ..., vn)) where n is the number of agents.
The "j" is the number of items allocated so far.
The "vi" are the value of bundle i to agent i.

Programmer: Erel Segal-Halevi
Since: 2021-11
"""

import dynprog, math
from typing import *


def egalitarian_value(valuation_matrix):
    """
    Returns the max-min value - does *not* return the partition itself.

    >>> egalitarian_value([[11,22,33,44],[11,22,33,44]])
    55
    >>> egalitarian_value([[11,22,33,44],[44,33,22,11]])
    77
    >>> #dynprog.logger.setLevel(logging.INFO)
    >>> egalitarian_value([[11,22,33,44,55],[44,33,22,11,55],[55,66,77,88,99]])
    77
    >>> egalitarian_value([[37,93,0,49,52,59,97,24,90],[62,21,31,27,67,29,24,65,47],[4,57,27,36,65,27,50,46,92]])
    187
    """
    # Algorithm: add the numbers one by one to all possible bundles.
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    def initial_states():  # returns (state,value) tuples
        zero_values = num_of_agents*(0,)
        yield ( (0, zero_values), -math.inf)
    def neighbors (state:Tuple[int,tuple], value:int):   # returns (state,value) tuples
        (item_index, bundle_values) = state
        if item_index < num_of_items:
            next_index = item_index+1
            for agent_index in range(num_of_agents):
                new_bundle_values = list(bundle_values)
                new_bundle_values[agent_index] += valuation_matrix[agent_index][item_index]
                state_value = -math.inf if next_index < num_of_items else min(new_bundle_values)
                yield ((next_index, tuple(new_bundle_values)), state_value)
    def is_final_state(state):
        return state[0]==num_of_items
    return dynprog.max_value(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)

def egalitarian_allocation(valuation_matrix):
    """
    Returns the max-min value and allocation

    >>> egalitarian_allocation([[11,22,33,44],[11,22,33,44]])
    (55, [[0, 3], [1, 2]])
    >>> egalitarian_allocation([[11,22,33,44],[44,33,22,11]])
    (77, [[2, 3], [0, 1]])
    >>> egalitarian_allocation([[11,22,33,44,55],[44,33,22,11,55],[55,66,77,88,99]])
    (77, [[2, 3], [0, 1], [4]])
    >>> egalitarian_allocation([[37,93,0,49,52,59,97,24,90],[62,21,31,27,67,29,24,65,47],[4,57,27,36,65,27,50,46,92]])
    (187, [[1, 6], [0, 2, 5, 7], [3, 4, 8]])
    """
    # Algorithm: add the numbers one by one to all possible bundles.
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    def initial_states():  # returns (state,value,data) tuples
        zero_values = num_of_agents*(0,)
        empty_allocation = num_of_agents*([],)
        yield ( (0, zero_values), -math.inf, empty_allocation)
    def neighbors (state:Tuple[int,tuple], value:int, allocation:list):   # returns (state,value,data) tuples
        (item_index, bundle_values) = state
        if item_index < num_of_items:
            next_index = item_index+1
            for agent_index in range(num_of_agents):
                new_bundle_values = list(bundle_values)
                new_bundle_values[agent_index] += valuation_matrix[agent_index][item_index]
                state_value = -math.inf if next_index < num_of_items else min(new_bundle_values)
                new_allocation = list(allocation)
                new_allocation[agent_index] = new_allocation[agent_index] + [item_index]
                yield ((next_index, tuple(new_bundle_values)), state_value, new_allocation)
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
    import numpy as np
    valuation_matrix = np.random.randint(0,99, [3,9])
    print("valuation_matrix:\n",valuation_matrix)
    print(egalitarian_allocation(valuation_matrix))
