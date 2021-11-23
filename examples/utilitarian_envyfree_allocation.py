#!python3

"""
Uses the generic dynamic programming function to find an envy-free allocation
of items to agents with different valuations, with a largest sum of utilities (utilitarian value).

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are of the form  (j, (v1, v2, ..., vn)) where n is the number of agents.
The "j" is the number of items allocated so far.
The "vi" are the value of bundle i to agent i.

Programmer: Erel Segal-Halevi
Since: 2021-11
"""

import dynprog, math, logging
from typing import *

logger = logging.getLogger(__name__)


def utilitarian_envyfree_value(valuation_matrix):
    """
    Returns the maximum utilitarian value in an envy-free allocation - does *not* return the allocation itself.
    Returns -inf if there is no envy-free allocation.

    >>> logger.setLevel(logging.WARNING)
    >>> dynprog.logger.setLevel(logging.WARNING)
    >>> utilitarian_envyfree_value([[11,0,11],[33,44,55]])
    110.0
    >>> utilitarian_envyfree_value([[11,22,33,44],[44,33,22,11]])
    154.0
    >>> utilitarian_envyfree_value([[11,0,11,11],[0,11,11,11],[33,33,33,33]])
    88.0
    >>> utilitarian_envyfree_value([[11],[22]])  # no envy-free allocation
    -inf
    """
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
            next_index = item_index+1
            for agent_index in range(num_of_agents):
                new_bundle_differences = [list(d) for d in bundle_differences]
                for other_agent_index in range(num_of_agents):
                    if other_agent_index==agent_index: continue
                    new_bundle_differences[agent_index][other_agent_index] += valuation_matrix[agent_index][item_index]
                    new_bundle_differences[other_agent_index][agent_index] -= valuation_matrix[other_agent_index][item_index]
                new_bundle_differences = tuple((tuple(d) for d in new_bundle_differences))
                state_value = -math.inf 
                if next_index == num_of_items and is_envyfree(new_bundle_differences): 
                    state_value = sum([sum(d) for d in new_bundle_differences])
                yield ((next_index, tuple(new_bundle_differences)), state_value)
    def is_final_state(state):
        (item_index, bundle_values) = state
        return item_index==num_of_items
    value = dynprog.max_value(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
    for i in range(num_of_agents):
        for j in range(num_of_items):
            value += valuation_matrix[i][j]
    value /= num_of_agents
    return value


# def utilitarian_envyfree_allocation(valuation_matrix):
#     """
#     Returns the utilitarian-maximum envy-free allocation and its utilitarian value.
#     Raises an exception if there is no envy-free allocation.
#
#     >>> dynprog.logger.setLevel(logging.WARNING)
#     >>> utilitarian_envyfree_allocation([[11,0,11],[0,11,22]])
#     (44, [[0], [1, 2]])
#     >>> utilitarian_envyfree_allocation([[11,22,33,44],[44,33,22,11]])
#     (154, [[2, 3], [0, 1]])
#     >>> utilitarian_envyfree_allocation([[11,0,11,11],[0,11,11,11],[33,33,33,33]])
#     (88, [[0], [1], [2, 3]])
#     >>> utilitarian_envyfree_allocation([[11],[11]]) 
#     Traceback (most recent call last):
#     ...
#     ValueError: No envyfree allocation
#     >>> utilitarian_envyfree_allocation([[37,20,34,12,71,17,55,97,79],[57,5,59,63,92,23,4,36,69],[16,3,41,42,68,47,60,39,17]])
#     (556, [[1, 7, 8], [0, 3, 4], [2, 5, 6]])
#     """
#     # Algorithm: add the items one by one to all possible bundles.
#     num_of_agents   = len(valuation_matrix)
#     num_of_items    = len(valuation_matrix[0])
#     thresholds = [sum(valuation_matrix[i])/num_of_agents for i in range(num_of_agents)]
#     logger.info("thresholds: %s", thresholds)
#     def is_envyfree(bundle_values:list)->bool:
#         return all([bundle_values[i]>=thresholds[i] for i in range(num_of_agents)])
#     def initial_states():  # returns (state,value,data) tuples
#         zero_values = num_of_agents*(0,)
#         empty_allocation = num_of_agents*([],)
#         yield ( (0, zero_values), -math.inf, empty_allocation)
#     def neighbors (state:Tuple[int,tuple], value:int, allocation:list):   # returns (state,value,data) tuples
#         (item_index, bundle_values) = state
#         if item_index < num_of_items:
#             next_index = item_index+1
#             for agent_index in range(num_of_agents):
#                 new_bundle_values = list(bundle_values)
#                 new_bundle_values[agent_index] += valuation_matrix[agent_index][item_index]
#                 state_value = -math.inf 
#                 if next_index == num_of_items and is_envyfree(new_bundle_values): state_value = sum(new_bundle_values)
#                 new_allocation = list(allocation)
#                 new_allocation[agent_index] = new_allocation[agent_index] + [item_index]
#                 yield ((next_index, tuple(new_bundle_values)), state_value, new_allocation)
#     def is_final_state(state):
#         (item_index, bundle_values) = state
#         return item_index==num_of_items
#     (state, value, data, num_of_states) = dynprog.max_value_solution(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
#     if value==-math.inf:
#         raise ValueError("No envyfree allocation")
#     else:
#         return (value,data)


if __name__=="__main__":
    import sys
    dynprog.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.logger.setLevel(logging.WARNING)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.logger.setLevel(logging.WARNING)
    import numpy as np
    valuation_matrix = np.random.randint(0,99, [3,9])
    print("valuation_matrix:\n",valuation_matrix)
    print(utilitarian_envyfree_value(valuation_matrix))
