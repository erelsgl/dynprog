#!python3
"""
Uses the sequential dynamic programming function to solve the multiple-subset-sum problem:
https://en.wikipedia.org/wiki/Multiple_subset_sum

Programmer: Erel Segal-Halevi
Since: 2021-12
"""

import dynprog
from typing import *



def max_sum(inputs: List[int], capacities:List[int])->int:
    """
    Returns the maximum sum of values from the given `inputs` list, 
        that can fit within m bin of the given capacities
        (m = len(capacities)).

    >>> max_sum([3,5], [2,2])
    0
    >>> max_sum([3,5], [4,4])
    3
    >>> max_sum([3,5], [6,6])
    8
    >>> max_sum([3,5], [8,8])
    8
    >>> max_sum([100,200,400,700,1100,1600,2200,2900,3700], [2005,2006])
    4000
    """
    return dynprog.sequential.max_value(
        inputs,
        initial_states = _initial_states(len(capacities)),
        transition_functions = _transition_functions(len(capacities)),
        value_function = _value_function,
        filter_functions = _filter_functions(capacities)
    )


def max_sum_solution(inputs: List[int], capacities:List[int])->int:
    """
    Returns the maximum sum of values from the given `inputs` list, that can fit within a bin of the given 'capacity'.

    >>> max_sum_solution([3,5], [2,2])
    [[], []]
    >>> max_sum_solution([3,5], [4,4])
    [[3], []]
    >>> max_sum_solution([3,5], [6,6])
    [[5], [3]]
    >>> max_sum_solution([3,5], [8,8])
    [[3, 5], []]
    >>> max_sum_solution([100,200,400,700,1100,1600,2200,2900,3700], [2005,2006])
    [[400, 1600], [200, 700, 1100]]
    """
    return dynprog.sequential.max_value_solution(
        inputs,
        initial_states = _initial_states(len(capacities)),
        transition_functions = _transition_functions(len(capacities)),
        value_function = _value_function,
		initial_solution = _initial_solution(len(capacities)),
		construction_functions = _construction_functions(len(capacities)),
        filter_functions = _filter_functions(capacities)
    )[2]



# Common definitions:

def _initial_states(num_of_bins:int):
    zero_values = num_of_bins*(0,)
    return [zero_values]

def _initial_solution(num_of_bins:int):
    empty_bundles = [ [] for _ in range(num_of_bins)]
    return empty_bundles


   
def _add_input_to_bin_sum(bin_sums:list, bin_index:int, input:int):
    """
    Adds the given input integer to bin #bin_index in the given list of bins.
    >>> _add_input_to_bin_sum([11, 22, 33], 0, 77)
    [88, 22, 33]
    >>> _add_input_to_bin_sum([11, 22, 33], 1, 77)
    [11, 99, 33]
    >>> _add_input_to_bin_sum([11, 22, 33], 2, 77)
    [11, 22, 110]
    """
    new_bin_sums = list(bin_sums)
    new_bin_sums[bin_index] = new_bin_sums[bin_index] + input
    return new_bin_sums
def _transition_functions(num_of_bins:int):
    """
    >>> for f in _transition_functions(3): f([11,22,33],77)
    [11, 22, 33]
    [88, 22, 33]
    [11, 99, 33]
    [11, 22, 110]
    """
    return [
        lambda state, input: state    # do not add the input at all
    ] + [
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
    return  [
        lambda solution, input: solution    # do not add the input at all
    ] + [
        lambda solution,input,bin_index=bin_index: _add_input_to_bin(solution, bin_index, input)
        for bin_index in range(num_of_bins)
    ]


_value_function = lambda state: sum(state)


def _filter_functions(capacities:List[int]):
    num_of_bins = len(capacities)
    return  [
        lambda state,input: True    # do not add the input at all
    ] +  [
        lambda state,input,bin_index=bin_index: state[bin_index]+input <= capacities[bin_index]
        for bin_index in range(num_of_bins)
    ]




if __name__=="__main__":
    import sys, logging
    dynprog.sequential.logger.addHandler(logging.StreamHandler(sys.stdout))
    dynprog.sequential.logger.setLevel(logging.WARNING)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

