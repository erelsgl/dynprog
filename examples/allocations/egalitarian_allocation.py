#!python3

"""
Uses the sequential dynamic programming function to find an egalitarian (max-min)
allocation of items to agents with different valuations.

This is a generalization of max_min_partition.py.

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

Programmer: Erel Segal-Halevi
Since: 2021-12
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
    num_of_agents   = len(valuation_matrix)
    return dynprog.sequential.max_value(
        inputs = _items_as_value_vectors(valuation_matrix),
        initial_states = _initial_states(num_of_agents),
        transition_functions = _transition_functions(num_of_agents),
        value_function = _value_function,
        filter_functions = None
    )


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
    num_of_agents   = len(valuation_matrix)
    (best_state,best_value,best_solution,num_of_states) = dynprog.sequential.max_value_solution(
        inputs = _items_as_value_vectors(valuation_matrix),
        initial_states = _initial_states(num_of_agents),
        transition_functions = _transition_functions(num_of_agents),
        value_function = _value_function,
		initial_solution=_initial_solution(num_of_agents),
		construction_functions = _construction_functions(num_of_agents),
        filter_functions = None
    )
    return (best_value,best_solution)



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
    (state, value, data, num_of_states) = dynprog.general.max_value_solution(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
    return (value,data)


def _items_as_value_vectors(valuation_matrix):
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    return [  # Each item is represented by a vector of values - a value for each agent. The last value is the item index.
        [valuation_matrix[agent_index][item_index] for agent_index in range(num_of_agents)] + [item_index]
        for item_index in range(num_of_items)
    ]



def _initial_states(num_of_agents:int):
    zero_values = num_of_agents*(0,)
    return {zero_values}

def _initial_solution(num_of_agents:int):
    empty_bundles = [ [] for _ in range(num_of_agents)]
    return empty_bundles



def _add_input_to_agent_value(agent_values:list, agent_index:int, input:int):
    """
    Adds the given item to agent #agent_index.
    >>> _add_input_to_agent_value([11, 22, 33], 0, [55,66,77,1])
    (66, 22, 33)
    >>> _add_input_to_agent_value([11, 22, 33], 1, [55,66,77,1])
    (11, 88, 33)
    >>> _add_input_to_agent_value([11, 22, 33], 2, [55,66,77,1])
    (11, 22, 110)
    """
    new_agent_values = list(agent_values)
    new_agent_values[agent_index] = new_agent_values[agent_index] + input[agent_index]
    return tuple(new_agent_values)
def _transition_functions(num_of_agents:int):
    """
    >>> for f in _transition_functions(3): f([11,22,33],[55,66,77,1])
    (66, 22, 33)
    (11, 88, 33)
    (11, 22, 110)
    """
    return [
        lambda state, input, agent_index=agent_index: _add_input_to_agent_value(state, agent_index, input)
        for agent_index in range(num_of_agents)
    ]


def _add_input_to_bin(bins:list, agent_index:int, input:int):
    """
    Adds the given input integer to bin #agent_index in the given list of bins.
    >>> _add_input_to_bin([[11,22], [33,44], [55,66]], 1, [55, 66, 77,1])
    [[11, 22], [33, 44, 1], [55, 66]]
    """
    new_bins = list(bins)
    item_index = input[-1]
    new_bins[agent_index] = new_bins[agent_index]+[item_index]
    return new_bins
def _construction_functions(num_of_agents:int):
    return [
        lambda solution,input,agent_index=agent_index: _add_input_to_bin(solution, agent_index, input)
        for agent_index in range(num_of_agents)
    ]


_value_function = lambda state: min(state)





if __name__=="__main__":
    import sys, logging
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.sequential.logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.sequential.logger.setLevel(logging.INFO)
    import numpy as np
    valuation_matrix = np.random.randint(0,9, [3,10]) # 3 agents, 10 items
    print("valuation_matrix:\n",valuation_matrix)
    print(egalitarian_value(valuation_matrix))
    print(egalitarian_allocation(valuation_matrix))
    # Should have about 30k-40k states.
