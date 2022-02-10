#!python3

"""
Uses the sequential dynamic programming function to find an EF1/EFx allocation
of items to agents with different valuations, with a largest sum of utilities (utilitarian value).

The input is a valuation-matrix v, where v[i][j] is the value of agent i to item j.

The states are of the form (d11, d12, ..., dnn; b11, b12, ..., bnn) where n is the number of agents.
where dij := vi(Ai)-vi(Aj).
and   bij is the largest value for i of an item allocated to j.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog, math, logging
from typing import *
from dynprog.sequential import SequentialDynamicProgram

from common import (
    add_input_to_agent_value,
    add_input_to_bin,
    items_as_value_vectors,
)

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
    items = items_as_value_vectors(valuation_matrix)
    return PartitionDP(valuation_matrix, efx).max_value(items)


#### Dynamic program definition:


class PartitionDP(SequentialDynamicProgram):

    # The states are of the form (d11, d12, ..., dnn; b11, b12, ..., bnn) where n is the number of agents.
    # where dij := vi(Ai)-vi(Aj).
    # and   bij is the largest value for i of an item allocated to j.

    def __init__(self, valuation_matrix, efx=False):
        num_of_agents = self.num_of_agents = len(valuation_matrix)
        self.thresholds = [
            sum(valuation_matrix[i]) / num_of_agents
            for i in range(num_of_agents)
        ]
        self.valuation_matrix = valuation_matrix
        self.sum_valuation_matrix = sum(map(sum, valuation_matrix))
        self.efx = efx

    def initial_states(self):
        zero_differences = self.num_of_agents * (self.num_of_agents * (0,),)
        # print("zero_differences",zero_differences)
        initial_value_to_remove = math.inf if self.efx else 0
        largest_value_owned_by_others = self.num_of_agents * (
            self.num_of_agents * (initial_value_to_remove,),
        )
        return {(zero_differences, largest_value_owned_by_others)}

    def initial_solution(self):
        empty_bundles = [[] for _ in range(self.num_of_agents)]
        return empty_bundles

    def transition_functions(self):
        return [
            lambda state, input, agent_index=agent_index: (
                _update_bundle_differences(state[0], agent_index, input),
                _update_value_owned_by_others(
                    state[1],
                    agent_index,
                    input[-1],
                    self.valuation_matrix,
                    self.efx,
                ),
            )
            for agent_index in range(self.num_of_agents)
        ]

    def construction_functions(self):
        return [
            lambda solution, input, agent_index=agent_index: add_input_to_bin(
                solution, agent_index, input[-1]
            )
            for agent_index in range(self.num_of_agents)
        ]

    def value_function(self):
        return (
            lambda state: (sum(map(sum, state[0])) + self.sum_valuation_matrix)
            / self.num_of_agents
            if self._is_ef1(state[0], state[1])
            else -math.inf
        )

    def _is_ef1(
        self, bundle_differences: list, largest_value_owned_by_others: list
    ) -> bool:
        return all(
            [
                bundle_differences[i][j] + largest_value_owned_by_others[i][j]
                >= 0
                for i in range(self.num_of_agents)
                for j in range(self.num_of_agents)
            ]
        )


def _update_bundle_differences(bundle_differences, agent_index, item_values):
    """
    >>> _update_bundle_differences( ((0,0),(0,0)), 0, [11,33,0]  )
    ((0, 11), (-33, 0))
    >>> _update_bundle_differences( ((0,0),(0,0)), 1, [11,33,0]  )
    ((0, -11), (33, 0))
    """
    # print("bundle_differences",bundle_differences)
    num_of_agents = len(bundle_differences)
    new_bundle_differences = [list(d) for d in bundle_differences]
    for other_agent_index in range(num_of_agents):
        if other_agent_index == agent_index:
            continue
        new_bundle_differences[agent_index][other_agent_index] += item_values[
            agent_index
        ]
        new_bundle_differences[other_agent_index][agent_index] -= item_values[
            other_agent_index
        ]
    new_bundle_differences = tuple((tuple(d) for d in new_bundle_differences))
    return new_bundle_differences


def _update_value_owned_by_others(
    largest_value_owned_by_others: list,
    agent_index: int,
    item_index: int,
    valuation_matrix,
    efx=False,
):
    """
    Update the matrix of largest-value-owned-by-others when
    the item #item_index is given to the agent #agent_index.
    >>> _update_value_owned_by_others([[0,0,0],[0,0,0],[0,0,0]], 0, 0, [[55,66,77],[88,99,11],[22,33,44]])
    ((0, 0, 0), (88, 0, 0), (22, 0, 0))
    >>> _update_value_owned_by_others([[0,20,30],[40,0,60],[70,80,0]], 0, 0, [[55,66,77],[88,99,11],[22,33,44]])
    ((0, 20, 30), (88, 0, 60), (70, 80, 0))
    """
    num_of_agents = len(largest_value_owned_by_others)
    new_largest_value_owned_by_others = [
        list(d) for d in largest_value_owned_by_others
    ]
    for other_agent_index in range(num_of_agents):
        if other_agent_index == agent_index:
            continue
        other_agent_value = valuation_matrix[other_agent_index][item_index]
        if efx:
            replace_item = (
                other_agent_value
                < new_largest_value_owned_by_others[other_agent_index][
                    agent_index
                ]
            )
        else:  # ef1
            replace_item = (
                other_agent_value
                > new_largest_value_owned_by_others[other_agent_index][
                    agent_index
                ]
            )
        if replace_item:
            new_largest_value_owned_by_others[other_agent_index][
                agent_index
            ] = other_agent_value
    new_largest_value_owned_by_others = tuple(
        (tuple(d) for d in new_largest_value_owned_by_others)
    )
    return new_largest_value_owned_by_others


if __name__ == "__main__":
    import sys, doctest, random

    dynprog.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.logger.setLevel(logging.WARNING)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.WARNING)

    (failures, tests) = doctest.testmod(report=True)
    print("{} failures, {} tests".format(failures, tests))

    dynprog.logger.setLevel(logging.INFO)

    valuation_matrix = [
        [random.randint(0, 9) for _ in range(10)] for _ in range(3)
    ]  # ~ 80k states
    print("valuation_matrix:\n", valuation_matrix)
    print("Utilitarian within EF1: ", utilitarian_ef1_value(valuation_matrix))
    print(
        "Utilitarian within EFx: ",
        utilitarian_ef1_value(valuation_matrix, efx=True),
    )
