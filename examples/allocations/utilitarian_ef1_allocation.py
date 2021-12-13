#!python3

"""
Uses the generic dynamic programming function to find an EF1/EFx allocation
of items to agents with different valuations, with a largest sum of utilities (utilitarian value).

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are of the form  (j, (v1, v2, ..., vn)) where n is the number of agents.
The "j" is the number of items allocated so far.
The "vi" are the value of bundle i to agent i.

Programmer: Erel Segal-Halevi
Since: 2021-11
"""

import dynprog, math, logging, itertools
from typing import *

logger = logging.getLogger(__name__)


def utilitarian_ef1_value(valuation_matrix, efx=False):
    """
    Returns the maximum utilitarian value in a ef1 allocation - does *not* return the partition itself.

    >>> dynprog.logger.setLevel(logging.WARNING)
    >>> utilitarian_ef1_value([[11,0,11],[33,44,55]])
    110.0
    >>> utilitarian_ef1_value([[11,0,11],[33,44,55]],efx=True)
    110.0
    >>> utilitarian_ef1_value([[11,22,33,44],[44,33,22,11]])
    154.0
    >>> utilitarian_ef1_value([[11,22,33,44],[44,33,22,11]],efx=True)
    154.0
    >>> utilitarian_ef1_value([[11,0,11,11],[0,11,11,11],[33,33,33,33]])
    88.0
    >>> utilitarian_ef1_value([[11,0,11,11],[0,11,11,11],[33,33,33,33]],efx=True)
    88.0
    >>> utilitarian_ef1_value([[11],[22]]) 
    22.0
    >>> utilitarian_ef1_value([[11],[22]],efx=True)
    22.0
    >>> utilitarian_ef1_value([[98,91,29,50,76,94],[43,67,93,35,49,12],[45,10,62,47,82,60]])
    505.0
    >>> utilitarian_ef1_value([[98,91,29,50,76,94],[43,67,93,35,49,12],[45,10,62,47,82,60]],efx=True)
    481.0
    """
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    def is_ef1(bundle_differences:List[List], largest_value_owned_by_others:List[List])->bool:
        return all([bundle_differences[i][j] + largest_value_owned_by_others[i][j]>=0 
            for i in range(num_of_agents) for j in range(num_of_agents)])
    def initial_states():  # returns (state,value) tuples
        zero_values = num_of_agents * (num_of_agents*(0,),)
        initial_value_to_remove = math.inf if efx else 0
        largest_value_owned_by_others = num_of_agents * (num_of_agents*(initial_value_to_remove,),)
        yield ( (0, zero_values, largest_value_owned_by_others), -math.inf)
    def neighbors (state:Tuple[int,tuple,tuple], value:int):   # returns (state,value) tuples
        (item_index, bundle_differences, largest_value_owned_by_others) = state
        if item_index < num_of_items:
            next_item_index = item_index+1
            for agent_index in range(num_of_agents): # consider giving item item_index to agent agent_index
                # Update bundle differences
                new_bundle_differences = [list(d) for d in bundle_differences]
                for other_agent_index in range(num_of_agents):
                    if other_agent_index==agent_index: continue
                    new_bundle_differences[agent_index][other_agent_index] += valuation_matrix[agent_index][item_index]
                    new_bundle_differences[other_agent_index][agent_index] -= valuation_matrix[other_agent_index][item_index]
                new_bundle_differences = tuple((tuple(d) for d in new_bundle_differences))

                # Update value owned by others
                new_largest_value_owned_by_others = [list(d) for d in largest_value_owned_by_others]
                for other_agent_index in range(num_of_agents):
                    if other_agent_index==agent_index: continue
                    other_agent_value = valuation_matrix[other_agent_index][item_index]
                    if efx:
                        replace_item = other_agent_value < new_largest_value_owned_by_others[other_agent_index][agent_index]
                    else: # ef1
                        replace_item = other_agent_value > new_largest_value_owned_by_others[other_agent_index][agent_index]
                    if replace_item:
                        new_largest_value_owned_by_others[other_agent_index][agent_index] = other_agent_value
                new_largest_value_owned_by_others = tuple((tuple(d) for d in new_largest_value_owned_by_others))
                
                # Check ef1:
                state_value = -math.inf 
                if next_item_index==num_of_items and is_ef1(new_bundle_differences,new_largest_value_owned_by_others): 
                    state_value = sum(map(sum,new_bundle_differences))
                yield ((next_item_index, new_bundle_differences, new_largest_value_owned_by_others), state_value)
    def is_final_state(state):
        (item_index, _, _) = state
        return item_index==num_of_items
    value = dynprog.general.max_value(initial_states=initial_states, neighbors=neighbors, is_final_state=is_final_state)
    if value==-math.inf:
        raise ValueError("No EF1 allocation -- this must be a bug")
    return (value + sum(map(sum,valuation_matrix))) / num_of_agents



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
    valuation_matrix = np.random.randint(0,99, [3,6])   # ~ 1093 states
    # valuation_matrix = np.random.randint(0,99, [3,7])   # ~ 3280 states
    print("valuation_matrix:\n",valuation_matrix)
    print("EF1: ",utilitarian_ef1_value(valuation_matrix))
    print("EFx: ",utilitarian_ef1_value(valuation_matrix,efx=True))
