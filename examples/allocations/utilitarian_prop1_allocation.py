#!python3

"""
Uses the generic dynamic programming function to find a PROP1 or PROPx allocation
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


def utilitarian_prop1_value(valuation_matrix, propx=False):
    """
    Returns the maximum utilitarian value in a PROP1 allocation - does *not* return the partition itself.

    >>> dynprog.general.logger.setLevel(logging.WARNING)
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
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    thresholds = [sum(valuation_matrix[i])/num_of_agents for i in range(num_of_agents)]
    logger.info("thresholds: %s", thresholds)
    def is_prop1(bundle_values:list,largest_value_owned_by_others:list)->bool:
        return all([bundle_values[i] + largest_value_owned_by_others[i] >= thresholds[i] for i in range(num_of_agents)])
    def initial_states():  # returns (state,value) tuples
        zero_values = num_of_agents*(0,)
        initial_value_to_remove = math.inf if propx else 0
        largest_value_owned_by_others = num_of_agents*(initial_value_to_remove,)
        yield ( (0, zero_values, largest_value_owned_by_others), -math.inf)
    def neighbors (state:Tuple[int,tuple,tuple], value:int):   # returns (state,value) tuples
        (item_index, bundle_values, largest_value_owned_by_others) = state
        if item_index < num_of_items:
            next_item_index = item_index+1
            for agent_index in range(num_of_agents): # consider giving item item_index to agent agent_index
                # Update my value
                new_bundle_values = list(bundle_values)
                new_bundle_values[agent_index] += valuation_matrix[agent_index][item_index]

                # Update value owned by others
                new_largest_value_owned_by_others = list(largest_value_owned_by_others)
                for other_agent_index in range(num_of_agents):
                    if other_agent_index!=agent_index:
                        other_agent_value = valuation_matrix[other_agent_index][item_index]
                        if propx:
                            replace_item = other_agent_value < new_largest_value_owned_by_others[other_agent_index]
                        else: # prop1
                            replace_item = other_agent_value > new_largest_value_owned_by_others[other_agent_index]
                        if replace_item:
                            new_largest_value_owned_by_others[other_agent_index] = other_agent_value
                
                # Check PROP1:
                state_value = -math.inf 
                if next_item_index==num_of_items and is_prop1(new_bundle_values,new_largest_value_owned_by_others): 
                    state_value = sum(new_bundle_values)

                yield ((next_item_index, tuple(new_bundle_values), tuple(new_largest_value_owned_by_others)), state_value)
    def is_final_state(state):
        (item_index, _, _) = state
        return item_index==num_of_items
    value = dynprog.general.max_value(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
    if value==-math.inf:
        raise ValueError("No PROP1 allocation -- this must be a bug")
    return value


def utilitarian_prop1_allocation(valuation_matrix, propx=False):
    """
    Returns the utilitarian-maximum PROP1 allocation and its utilitarian value.

    >>> dynprog.general.logger.setLevel(logging.WARNING)
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
    (88, [[0], [1], [2, 3]])
    >>> utilitarian_prop1_allocation([[11],[22]]) 
    (22, [[], [0]])
    >>> utilitarian_prop1_allocation([[11],[22]], propx=True)
    (22, [[], [0]])
    >>> utilitarian_prop1_allocation([[37,20,34,12,71,17,55,97,79],[57,5,59,63,92,23,4,36,69],[16,3,41,42,68,47,60,39,17]])
    (574, [[1, 7, 8], [0, 2, 3, 4], [5, 6]])
    >>> utilitarian_prop1_allocation([[37,20,34,12,71,17,55,97,79],[57,5,59,63,92,23,4,36,69],[16,3,41,42,68,47,60,39,17]], propx=True)
    (557, [[7, 8], [0, 2, 3, 4], [1, 5, 6]])
    """
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    thresholds = [sum(valuation_matrix[i])/num_of_agents for i in range(num_of_agents)]
    logger.info("thresholds: %s", thresholds)
    def is_prop1(bundle_values:list,largest_value_owned_by_others:list)->bool:
        return all([bundle_values[i] + largest_value_owned_by_others[i] >= thresholds[i] for i in range(num_of_agents)])
    def initial_states():  # returns (state,value,data) tuples
        zero_values = num_of_agents*(0,)
        empty_allocation = num_of_agents*([],)
        initial_value_to_remove = math.inf if propx else 0
        largest_value_owned_by_others = num_of_agents*(initial_value_to_remove,)
        yield ( (0, zero_values, largest_value_owned_by_others), -math.inf, empty_allocation)
    def neighbors (state:Tuple[int,tuple], value:int, allocation:list):   # returns (state,value,data) tuples
        (item_index, bundle_values, largest_value_owned_by_others) = state
        if item_index < num_of_items:
            next_item_index = item_index+1
            for agent_index in range(num_of_agents):

                # Update my value
                new_bundle_values = list(bundle_values)
                new_bundle_values[agent_index] += valuation_matrix[agent_index][item_index]

                # Update value owned by others
                new_largest_value_owned_by_others = list(largest_value_owned_by_others)
                for other_agent_index in range(num_of_agents):
                    if other_agent_index!=agent_index:
                        other_agent_value = valuation_matrix[other_agent_index][item_index]
                        if propx:
                            replace_item = other_agent_value < new_largest_value_owned_by_others[other_agent_index]
                        else: # prop1
                            replace_item = other_agent_value > new_largest_value_owned_by_others[other_agent_index]
                        if replace_item:
                            new_largest_value_owned_by_others[other_agent_index] = other_agent_value
                
                # Check PROP1:
                state_value = -math.inf 
                if next_item_index==num_of_items and is_prop1(new_bundle_values,new_largest_value_owned_by_others): 
                    state_value = sum(new_bundle_values)

                # Update allocation:
                new_allocation = list(allocation)
                new_allocation[agent_index] = new_allocation[agent_index] + [item_index]

                yield ((next_item_index, tuple(new_bundle_values), tuple(new_largest_value_owned_by_others)), state_value, new_allocation)

    def is_final_state(state):
        (item_index, _, _) = state
        return item_index==num_of_items
    (state, value, data, num_of_states) = dynprog.general.max_value_solution(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
    if value==-math.inf:
        raise ValueError("No PROP1 allocation -- this must be a bug")
    else:
        return (value,data)


if __name__=="__main__":
    import sys
    dynprog.general.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.general.logger.setLevel(logging.WARNING)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    dynprog.general.logger.setLevel(logging.WARNING)
    import numpy as np
    # valuation_matrix = np.random.randint(0,99, [3,6])   # ~ 1000 states
    valuation_matrix = np.random.randint(0,99, [3,7])   # ~ 3000 states
    print("valuation_matrix:\n",valuation_matrix)
    print(utilitarian_prop1_allocation(valuation_matrix))
