#!python3

"""
Uses the sequential dynamic programming function to find a PROP1 or PROPx allocation
of items to agents with different valuations, with a largest sum of utilities (utilitarian value).

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are of the form  (v1, v2, ..., vn; b1, b2, ..., bn) where n is the number of agents.
The "vi" are the value of bundle i to agent i.
The "bi" are the largest value for i of an item allocated to others.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""


import dynprog
from dynprog.sequential import SequentialDynamicProgram

import math, logging
from typing import *

from common import add_input_to_agent_value, add_input_to_bin, items_as_value_vectors

logger = logging.getLogger(__name__)


def utilitarian_prop1_value(valuation_matrix, propx=False):
    """
    Returns the maximum utilitarian value in a PROP1 allocation - does *not* return the partition itself.

    >>> utilitarian_prop1_value([[11,0,11],[33,44,55]])
    132
    >>> utilitarian_prop1_value([[11,0,11],[33,44,55]],propx=True)
    110
    >>> utilitarian_prop1_value([[11,22,33,44],[44,33,22,11]])
    154
    >>> utilitarian_prop1_value([[11,22,33,44],[44,33,22,11]],propx=True)
    154
    >>> utilitarian_prop1_value([[11,0,11,11],[0,11,11,11],[33,33,33,33]])
    132
    >>> utilitarian_prop1_value([[11,0,11,11],[0,11,11,11],[33,33,33,33]],propx=True)
    88
    >>> utilitarian_prop1_value([[11],[22]]) 
    22
    >>> utilitarian_prop1_value([[11],[22]],propx=True)
    22
    """
    items = items_as_value_vectors(valuation_matrix)
    return PartitionDP(valuation_matrix, propx).max_value(items)


def utilitarian_prop1_allocation(valuation_matrix, propx=False):
    """
    Returns the utilitarian-maximum PROP1 allocation and its utilitarian value.

    >>> dynprog.sequential.logger.setLevel(logging.WARNING)
    >>> utilitarian_prop1_allocation([[11,0,11],[33,44,55]])
    (132, [[], [0, 1, 2]])
    >>> utilitarian_prop1_allocation([[11,0,11],[33,44,55]], propx=True)
    (110, [[0], [1, 2]])
    >>> utilitarian_prop1_allocation([[11,22,33,44],[44,33,22,11]])
    (154, [[2, 3], [0, 1]])
    >>> utilitarian_prop1_allocation([[11,22,33,44],[44,33,22,11]], propx=True)
    (154, [[2, 3], [0, 1]])
    >>> utilitarian_prop1_allocation([[11,0,11,11],[0,11,11,11],[33,33,33,33]])
    (132, [[], [], [0, 1, 2, 3]])
    >>> utilitarian_prop1_allocation([[11,0,11,11],[0,11,11,11],[33,33,33,33]], propx=True)
    (88, [[3], [2], [0, 1]])
    >>> utilitarian_prop1_allocation([[11],[22]]) 
    (22, [[], [0]])
    >>> utilitarian_prop1_allocation([[11],[22]], propx=True)
    (22, [[], [0]])
    >>> utilitarian_prop1_allocation([[37,20,34,12,71,17,55,97,79],[57,5,59,63,92,23,4,36,69],[16,3,41,42,68,47,60,39,17]])
    (574, [[1, 7, 8], [0, 2, 3, 4], [5, 6]])
    >>> utilitarian_prop1_allocation([[37,20,34,12,71,17,55,97,79],[57,5,59,63,92,23,4,36,69],[16,3,41,42,68,47,60,39,17]], propx=True)
    (557, [[7, 8], [0, 2, 3, 4], [1, 5, 6]])
    """
    items = items_as_value_vectors(valuation_matrix)
    (best_state,best_value,best_solution,num_of_states) = PartitionDP(valuation_matrix, propx).max_value_solution(items)
    if best_value==-math.inf:
        raise ValueError("No proportional allocation")
    return (best_value,best_solution)



#### Dynamic program definition:

class PartitionDP(SequentialDynamicProgram):

    # The states are of the form  (v1, v2, ..., vn; b1, b2, ..., bn) where n is the number of agents.
    # The "vi" are the value of bundle i to agent i.
    # The "bi" are the largest value for i of an item allocated to others.

    def __init__(self, valuation_matrix, propx=False):
        num_of_agents = self.num_of_agents = len(valuation_matrix)
        self.thresholds = [sum(valuation_matrix[i])/num_of_agents for i in range(num_of_agents)]
        self.valuation_matrix = valuation_matrix
        self.propx = propx

    def initial_states(self):
        zero_values = self.num_of_agents*(0,)
        initial_value_to_remove = math.inf if self.propx else 0
        largest_value_owned_by_others = self.num_of_agents*(initial_value_to_remove,)
        yield (zero_values, largest_value_owned_by_others)

    def initial_solution(self):
        empty_bundles = [ [] for _ in range(self.num_of_agents)]
        return empty_bundles
   
    def transition_functions(self):
        return [
            lambda state, input, agent_index=agent_index: \
                (add_input_to_agent_value(state[0], agent_index, input) , \
                _update_value_owned_by_others(state[1], agent_index, input[-1], self.valuation_matrix, self.propx) )
            for agent_index in range(self.num_of_agents)
        ]

    def construction_functions(self):
        return [
            lambda solution,input,agent_index=agent_index: add_input_to_bin(solution, agent_index, input[-1])
            for agent_index in range(self.num_of_agents)
        ]

    def value_function(self):
        return lambda state: sum(state[0]) if self._is_prop1(state[0], state[1]) else -math.inf
    
    def _is_prop1(self, bundle_values:list,largest_value_owned_by_others:list)->bool:
        return all([bundle_values[i] + largest_value_owned_by_others[i] >= self.thresholds[i] for i in range(self.num_of_agents)])





def _update_value_owned_by_others(largest_value_owned_by_others:list, agent_index:int, item_index:int, valuation_matrix, propx=False):
    """
    :param input: a list of values: input[i] represents the value of the current item for agent i.

    Adds the given item to agent #agent_index.
    >>> _update_value_owned_by_others([33, 44, 66], 0, 0, [[55,66,77],[88,99,11],[22,33,44]])
    (33, 88, 66)
    """
    logger.info(largest_value_owned_by_others)
    new_largest_value_owned_by_others = list(largest_value_owned_by_others)
    num_of_agents = len(largest_value_owned_by_others)
    for other_agent_index in range(num_of_agents):
        if other_agent_index!=agent_index:
            other_agent_value = valuation_matrix[other_agent_index][item_index]
            if propx:
                should_replace_item = other_agent_value < new_largest_value_owned_by_others[other_agent_index]
            else: # prop1
                should_replace_item = other_agent_value > new_largest_value_owned_by_others[other_agent_index]
            if should_replace_item:
                new_largest_value_owned_by_others[other_agent_index] = other_agent_value
    return tuple(new_largest_value_owned_by_others)






if __name__=="__main__":
    import sys
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.sequential.logger.setLevel(logging.WARNING)

    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.sequential.logger.setLevel(logging.WARNING)
    import numpy as np
    valuation_matrix = np.random.randint(0,99, [3,7])   # ~ 3000 states
    print("Valuation matrix:\n",valuation_matrix)
    # print("Utilitarian PROP1 value:",utilitarian_prop1_value(valuation_matrix))
    print("Utilitarian PROP1 allocation:",utilitarian_prop1_allocation(valuation_matrix))
    # print("Utilitarian PROPx value:",utilitarian_prop1_value(valuation_matrix,propx=True))
    print("Utilitarian PROPx allocation:",utilitarian_prop1_allocation(valuation_matrix,propx=True))
