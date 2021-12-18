#!python3

"""
Uses the sequential dynamic programming function to find an envy-free allocation
of items to agents with different valuations, with a largest sum of utilities (utilitarian value).

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are the bundle-differences: (d11, d12, ..., dnn) where n is the number of agents.
where dij := vi(Ai)-vi(Aj).

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog, math, logging
from dynprog.sequential import SequentialDynamicProgram

from common import add_input_to_bin, items_as_value_vectors

from typing import *

logger = logging.getLogger(__name__)


def utilitarian_envyfree_value(valuation_matrix):
    """
    Returns the maximum utilitarian value in an envy-free allocation - does *not* return the allocation itself.
    Returns -inf if there is no envy-free allocation.

    >>> logger.setLevel(logging.INFO)
    >>> dynprog.sequential.logger.setLevel(logging.INFO)
    >>> utilitarian_envyfree_value([[11,0,11],[33,44,55]])
    110.0
    >>> logger.setLevel(logging.WARNING)
    >>> dynprog.sequential.logger.setLevel(logging.WARNING)
    >>> utilitarian_envyfree_value([[11,22,33,44],[44,33,22,11]])
    154.0
    >>> utilitarian_envyfree_value([[11,0,11,11],[0,11,11,11],[33,33,33,33]])
    88.0
    >>> utilitarian_envyfree_value([[11],[22]])  # no envy-free allocation
    -inf
    """
    items = items_as_value_vectors(valuation_matrix)
    return PartitionDP(valuation_matrix).max_value(items)

    # Algorithm: add the items one by one to all possible bundles.
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    def is_envyfree(bundle_differences:list)->bool:
        return all([bundle_differences[i][j]>=0 for i in range(num_of_agents) for j in range(num_of_agents)])
    def initial_states():  # returns (state,value) tuples
        zero_differences = num_of_agents * (num_of_agents*(0,),)
        yield ( (0, zero_differences), -math.inf)
    def neighbors (state:Tuple[int,tuple], value:int):   # returns (state,value) tuples
        (item_index, bundle_differences) = state
        if item_index < num_of_items:
            next_item_index = item_index+1
            for agent_index in range(num_of_agents):
                # Update bundle differences
                new_bundle_differences = [list(d) for d in bundle_differences]
                for other_agent_index in range(num_of_agents):
                    if other_agent_index==agent_index: continue
                    new_bundle_differences[agent_index][other_agent_index] += valuation_matrix[agent_index][item_index]
                    new_bundle_differences[other_agent_index][agent_index] -= valuation_matrix[other_agent_index][item_index]
                new_bundle_differences = tuple((tuple(d) for d in new_bundle_differences))

                # Check envy-freeness:
                state_value = -math.inf 
                if next_item_index == num_of_items and is_envyfree(new_bundle_differences): 
                    state_value = sum(map(sum,new_bundle_differences))
                yield ((next_item_index, new_bundle_differences), state_value)
    def is_final_state(state):
        (item_index, _) = state
        return item_index==num_of_items
    value = dynprog.general.max_value(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
    return (value + sum(map(sum,valuation_matrix))) / num_of_agents



#### Dynamic program definition:

class PartitionDP(SequentialDynamicProgram):

    # The states are the bundle-differences: (d11, d12, ..., dnn) where n is the number of agents.
    # where dij := vi(Ai)-vi(Aj).

    def __init__(self, valuation_matrix):
        self.num_of_agents = len(valuation_matrix)
        self.valuation_matrix = valuation_matrix
        self.sum_valuation_matrix =  sum(map(sum,valuation_matrix))

    def initial_states(self):
        zero_differences = self.num_of_agents * (self.num_of_agents*(0,),)
        return {zero_differences}

    def initial_solution(self):
        empty_bundles = [ [] for _ in range(self.num_of_agents)]
        return empty_bundles
   
    def transition_functions(self):
        return [
            lambda state, input, agent_index=agent_index: _update_bundle_differences(state, agent_index, input)
            for agent_index in range(self.num_of_agents)
        ]

    def construction_functions(self):
        return [
            lambda solution,input,agent_index=agent_index: add_input_to_bin(solution, agent_index, input[-1])
            for agent_index in range(self.num_of_agents)
        ]

    def value_function(self):
        return lambda state: (sum(map(sum,state))+self.sum_valuation_matrix) / self.num_of_agents if self._is_envyfree(state) else -math.inf
    
    def _is_envyfree(self, bundle_differences:list)->bool:
        return all([bundle_differences[i][j]>=0 for i in range(self.num_of_agents) for j in range(self.num_of_agents)])



def _update_bundle_differences(bundle_differences, agent_index, item_values):
    """
    >>> _update_bundle_differences( ((0,0),(0,0)), 0, [11,33,0]  )
    ((0, 11), (-33, 0))
    >>> _update_bundle_differences( ((0,0),(0,0)), 1, [11,33,0]  )
    ((0, -11), (33, 0))
    """
    num_of_agents = len(bundle_differences)
    new_bundle_differences = [list(d) for d in bundle_differences]
    for other_agent_index in range(num_of_agents):
        if other_agent_index==agent_index: continue
        new_bundle_differences[agent_index][other_agent_index] += item_values[agent_index]
        new_bundle_differences[other_agent_index][agent_index] -= item_values[other_agent_index]
    new_bundle_differences = tuple((tuple(d) for d in new_bundle_differences))
    return new_bundle_differences




if __name__=="__main__":
    import sys
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.sequential.logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.general.logger.setLevel(logging.WARNING)
    import numpy as np
    valuation_matrix = np.random.randint(0,99, [3,9])
    print("valuation_matrix:\n",valuation_matrix)
    print(utilitarian_envyfree_value(valuation_matrix))
