#!python3

"""
Uses the sequential dynamic programming function to find an egalitarian (max-min)
allocation of items to agents with different valuations.

This is a generalization of max_min_partition.py.

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are of the form  (v1, v2, ..., vn) where n is the number of agents.
The "vi" are the value of bundle i to agent i.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""


import dynprog
from dynprog.sequential import SequentialDynamicProgram

from typing import *

from common import add_input_to_bin, add_input_to_agent_value


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
    items = _items_as_value_vectors(valuation_matrix)
    return EgalitarianDP(num_of_agents).max_value(items)



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
    items = _items_as_value_vectors(valuation_matrix)
    (best_state,best_value,best_solution,num_of_states) = EgalitarianDP(num_of_agents).max_value_solution(items)
    return (best_value,best_solution)


def _items_as_value_vectors(valuation_matrix):
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    return [  # Each item is represented by a vector of values - a value for each agent. The last value is the item index.
        [valuation_matrix[agent_index][item_index] for agent_index in range(num_of_agents)] + [item_index]
        for item_index in range(num_of_items)
    ]




#### Dynamic program definition:

class EgalitarianDP(SequentialDynamicProgram):

    # The states are of the form  (v1, v2, ..., vn) where n is the number of agents.
    # The "vi" are the value of bundle i to agent i.

    def __init__(self, num_of_agents:int):
        self.num_of_agents = num_of_agents

    def initial_states(self):
        zero_values = self.num_of_agents*(0,)
        return {zero_values}

    def initial_solution(self):
        empty_bundles = [ [] for _ in range(self.num_of_agents)]
        return empty_bundles
   
    def transition_functions(self):
        return [
            lambda state, input, agent_index=agent_index: add_input_to_agent_value(state, agent_index, input)
            for agent_index in range(self.num_of_agents)
        ]

    def construction_functions(self):
        return [
            lambda solution,input,agent_index=agent_index: add_input_to_bin(solution, agent_index, input[-1])
            for agent_index in range(self.num_of_agents)
        ]

    def value_function(self):
        return lambda state: min(state)





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
