#!python3

"""
Uses the sequential dynamic programming function to find a proportional allocation
of items to agents with different valuations, with a largest sum of utilities (utilitarian value).

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are of the form  (v1, v2, ..., vn) where n is the number of agents.
The "vi" are the value of bundle i to agent i.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog
from dynprog.sequential import SequentialDynamicProgram

import math, logging
from typing import *

from common import add_input_to_agent_value, add_input_to_bin, items_as_value_vectors

logger = logging.getLogger(__name__)


def utilitarian_proportional_value(valuation_matrix):
    """
    Returns the maximum utilitarian value in a proportional allocation - does *not* return the partition itself.
    Returns -inf if there is no proportional allocation.

    >>> dynprog.sequential.logger.setLevel(logging.WARNING)
    >>> logger.setLevel(logging.WARNING)
    >>> utilitarian_proportional_value([[11,0,11],[33,44,55]])
    110
    >>> utilitarian_proportional_value([[11,22,33,44],[44,33,22,11]])
    154
    >>> utilitarian_proportional_value([[11,0,11,11],[0,11,11,11],[33,33,33,33]])
    88
    >>> utilitarian_proportional_value([[11],[22]])  # no proportional allocation
    -inf
    """
    items = items_as_value_vectors(valuation_matrix)
    return PartitionDP(valuation_matrix).max_value(items)

def utilitarian_proportional_allocation(valuation_matrix):
    """
    Returns the utilitarian-maximum proportional allocation and its utilitarian value.
    Raises an exception if there is no proportional allocation.

    >>> dynprog.sequential.logger.setLevel(logging.WARNING)
    >>> utilitarian_proportional_allocation([[11,0,11],[0,11,22]])
    (44, [[0], [1, 2]])
    >>> utilitarian_proportional_allocation([[11,22,33,44],[44,33,22,11]])
    (154, [[2, 3], [0, 1]])
    >>> utilitarian_proportional_allocation([[11,0,11,11],[0,11,11,11],[33,33,33,33]])[0]
    88
    >>> utilitarian_proportional_allocation([[11],[11]]) 
    Traceback (most recent call last):
    ...
    ValueError: No proportional allocation
    >>> utilitarian_proportional_allocation([[37,20,34,12,71,17,55,97,79],[57,5,59,63,92,23,4,36,69],[16,3,41,42,68,47,60,39,17]])
    (556, [[1, 7, 8], [0, 3, 4], [2, 5, 6]])
    """
    items = items_as_value_vectors(valuation_matrix)
    (best_state,best_value,best_solution,num_of_states) = PartitionDP(valuation_matrix).max_value_solution(items)
    if best_value==-math.inf:
        raise ValueError("No proportional allocation")
    return (best_value,best_solution)


#### Dynamic program definition:

class PartitionDP(SequentialDynamicProgram):

    # The states are of the form  (v1, v2, ..., vn) where n is the number of agents.
    # The "vi" are the value of bundle i to agent i.

    def __init__(self, valuation_matrix):
        num_of_agents = self.num_of_agents = len(valuation_matrix)
        self.thresholds = [sum(valuation_matrix[i])/num_of_agents for i in range(num_of_agents)]

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
        return lambda state: sum(state) if self._is_proportional(state) else -math.inf
    
    def _is_proportional(self, bundle_values:list)->bool:
        return all([bundle_values[i] >= self.thresholds[i] for i in range(self.num_of_agents)])




if __name__=="__main__":
    import sys
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.sequential.logger.setLevel(logging.WARNING)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.sequential.logger.setLevel(logging.INFO)
    import numpy as np
    valuation_matrix = np.random.randint(0,9, [3,10])
    print("valuation_matrix:\n",valuation_matrix)
    print(utilitarian_proportional_value(valuation_matrix))
    print(utilitarian_proportional_allocation(valuation_matrix))
    # should have about 20k states.
