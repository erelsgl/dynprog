#!python3

"""
Uses the sequential dynamic programming function to solve the
max-min number partitioning problem.

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog
from typing import *


def max_min_value(items:List[int], num_of_bins:int):
    """
    Returns the max-min value - does *not* return the partition itself.

    >>> max_min_value([1,2,3,4], 2)
    5
    >>> max_min_value([1,2,3,4,5], 2)
    7
    >>> max_min_value([11,22,33,44,55,66,77,88,99], 3)
    165
    """
    return dynprog.sequential.max_value(
        inputs = items,
        initial_states = _initial_states(num_of_bins),
        transition_functions = _transition_functions(num_of_bins),
        value_function = _value_function,
        filter_functions = None
    )

def max_min_binition(items:list, num_of_bins:int):
    """
    Returns the max-min partition.

    >>> max_min_binition([1,2,3,4], 2)
    (5, [[1, 4], [2, 3]])
    >>> max_min_binition([1,2,3,4,5], 2)
    (7, [[3, 5], [1, 2, 4]])
    >>> max_min_binition([11,22,33,44,55,66,77,88,99], 3)
    (165, [[66, 99], [77, 88], [11, 22, 33, 44, 55]])
    """
    (best_state,best_value,best_solution,num_of_states) = dynprog.sequential.max_value_solution(
        inputs = items,
        initial_states = _initial_states(num_of_bins),
        transition_functions = _transition_functions(num_of_bins),
        value_function = _value_function,
		initial_solution=_initial_solution(num_of_bins),
		construction_functions = _construction_functions(num_of_bins),
        filter_functions = None
    )
    return (best_value,best_solution)





def _initial_states(num_of_bins:int):
    zero_values = num_of_bins*(0,)
    return {zero_values}

def _initial_solution(num_of_bins:int):
    empty_bundles = [ [] for _ in range(num_of_bins)]
    return empty_bundles



def _add_input_to_bin_sum(bin_sums:list, bin_index:int, input:int):
    """
    Adds the given input integer to bin #bin_index in the given list of bins.
    >>> _add_input_to_bin_sum([11, 22, 33], 0, 77)
    (88, 22, 33)
    >>> _add_input_to_bin_sum([11, 22, 33], 1, 77)
    (11, 99, 33)
    >>> _add_input_to_bin_sum([11, 22, 33], 2, 77)
    (11, 22, 110)
    """
    new_bin_sums = list(bin_sums)
    new_bin_sums[bin_index] = new_bin_sums[bin_index] + input
    return tuple(new_bin_sums)
def _transition_functions(num_of_bins:int):
    """
    >>> for f in _transition_functions(3): f([11,22,33],77)
    (88, 22, 33)
    (11, 99, 33)
    (11, 22, 110)
    """
    return [
        lambda state, input, bin_index=bin_index: _add_input_to_bin_sum(state, bin_index, input)
        for bin_index in range(num_of_bins)
    ]


def _add_input_to_bin(bins:list, bin_index:int, input:int):
    """
    Adds the given input integer to bin #bin_index in the given list of bins.
    >>> _add_input_to_bin([[11,22], [33,44], [55,66]], 1, 77)
    [[11, 22], [33, 44, 77], [55, 66]]
    """
    new_bins = list(bins)
    new_bins[bin_index] = new_bins[bin_index]+[input]
    return new_bins
def _construction_functions(num_of_bins:int):
    return [
        lambda solution,input,bin_index=bin_index: _add_input_to_bin(solution, bin_index, input)
        for bin_index in range(num_of_bins)
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
    print(max_min_value(5*[11]+5*[23], 2))
    print(max_min_binition(5*[11]+5*[23], 2))
    # Number of states should be around 100.
