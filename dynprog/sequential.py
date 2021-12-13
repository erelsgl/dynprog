#!python3

"""
A sequential dynamic program - a DP that handles the inputs one by one.

Based on the "Simple DP" defined by Gerhard J. Woeginger (2000) in:
   "When Does a Dynamic Programming Formulation Guarantee the Existence of a FPTAS?". 

Programmer: Erel Segal-Halevi.
Since: 2021-12
"""

from typing import *
from dataclasses import dataclass

Input = List[int]
State = List[int]
Value = float

import logging
logger = logging.getLogger(__name__)



def max_value(
    inputs: List[Input],
    initial_states:        List[State],                                 # S_0
    transition_functions:  List[Callable[[State, Input], State]],       # F
    value_function:        Callable[[State], Value],                    # g
    filter_functions:      List[Callable[[State, Input], bool]]=None,   # H
    ):
    """
    This is a shorter function that only returns the maximum value - it does not return the optimum solution.

    :param inputs: the list of inputs.
    :param initial_states: a set of initial states.
    :param transition_functions: a set of functions; each function maps a pair (state,input) to a new state.
    :param value_function:   a function that maps a state to its "value" (that should be maximized).
    :param filter_functions [optional]: a set of functions; each function maps a pair (state,input) to a boolean value which is "true" iff the new state should be added.
    """
    current_states = initial_states
    if filter_functions is None:
        filter_functions = _default_filter_functions(transition_functions)
    logger.info("%d initial states, %d transition functions.", len(current_states), len(transition_functions))
    num_of_processed_states = len(current_states)
    for input_index,input in enumerate(inputs):
        next_states = [
            f(state,input)
            for (f,h) in zip(transition_functions,filter_functions)
            for state in current_states
            if h(state,input)
        ]
        # logger.info("Processed input %d (%s) and added %d states: %s.", input_index, input, len(next_states), next_states)
        logger.info("Processed input %d (%s) and added %d states.", input_index, input, len(next_states))
        num_of_processed_states += len(next_states)
        current_states = next_states
    logger.info("Processed %d states.", num_of_processed_states)
    if len(current_states)==0:
        raise ValueError("No final states!")
    return max([value_function(state) for state in current_states])


Solution=Any

def max_value_solution(
    inputs: List[Input],
    initial_states:         List[State],                                 # S_0
    transition_functions:   List[Callable[[State, Input], State]],       # F
    value_function:         Callable[[State], Value],                    # g
    initial_solution:       Solution,
    construction_functions: List[Callable[[Solution, Input], Solution]],
    filter_functions:       List[Callable[[State, Input], bool]]=None,   # H
    ):
    """
    This function returns both the maximum value and the corresponding optimum solution.

    :param inputs: the list of inputs.
    :param initial_states: a set of initial states.
    :param transition_functions: a list of functions; each function maps a pair (state,input) to a new state.
    :param value_function:   a function that maps a state to its "value" (that should be maximized).
    :param initial_solution: the initial value for constructing the actual solution.
    :param construction_functions: a list of functions; each function maps a pair (solution,input) to a new solution, resulting from adding the input.
    :param filter_functions [optional]: a list of functions; each function maps a pair (state,input) to a boolean value which is "true" iff the new state should be added.
    """

    @dataclass
    class StateRecord:
        state: State
        prev:  Any #StateRecord
        transition_index: int  # the index of the transition function used to go from prev to state.

    current_state_records = [StateRecord(state,None,None) for state in initial_states] # Add a link to the 'previous state', which is initially None.
    if filter_functions is None:
        filter_functions = _default_filter_functions(transition_functions)
    logger.info("%d initial states, %d transition functions.", len(current_state_records), len(transition_functions))
    num_of_processed_states = len(current_state_records)
    for input_index,input in enumerate(inputs):
        next_state_records = [
            StateRecord(f(record.state,input), record, transition_index)
            for (transition_index,(f,h)) in enumerate(zip(transition_functions,filter_functions))
            for record in current_state_records
            if h(record.state, input)
        ]
        logger.info("Processed input %d (%s) and added %d states.", input_index, input, len(next_state_records))
        num_of_processed_states += len(next_state_records)
        current_state_records = next_state_records
    logger.info("Processed %d states.", num_of_processed_states)

    if len(current_state_records)==0:
        raise ValueError("No final states!")

    best_final_record = max(current_state_records, key=lambda record: value_function(record.state))
    best_final_state = best_final_record.state
    best_final_state_value = value_function(best_final_state)

    # construct path to solution
    path = []
    record = best_final_record
    while record.prev is not None:
        path.insert(0, record.transition_index)
        record = record.prev
    logger.info("Path to best solution: %s", path)

    # construct solution
    solution = initial_solution
    for input_index,input in enumerate(inputs):
        transition_index = path[input_index]
        logger.info("input %d (%s): transition %d", input_index, input, transition_index)
        solution = construction_functions[transition_index](solution, input)
    
    return (best_final_state, best_final_state_value, solution, num_of_processed_states)



def _default_filter_functions(transition_functions):
    return [(lambda state,input: True) for _ in transition_functions]




if __name__=="__main__":
    import sys
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

    # Example: subset sum.
    inputs = [100,200,400,700,1100,1600,2200,2900,3700]
    capacity = 4005

    print(max_value(
        inputs = inputs,
        initial_states=[0],
        transition_functions=[
            lambda state,input: state+input,    # adding the input
            lambda state,input: state+0,        # not adding the input
        ],
        value_function = lambda state: state,
        filter_functions = [
            lambda state,input: state+input<=capacity,    # adding the input
            lambda state,input: True,                     # not adding the input
        ]
    ))

    print(max_value_solution(
        inputs = inputs,
        initial_states=[0],
        transition_functions=[
            lambda state,input: state+input,    # adding the input
            lambda state,_:     state+0,        # not adding the input
        ],
        value_function = lambda state: state,
        initial_solution = [],
        construction_functions = [
            lambda solution,input: solution+[input],    # adding the input
            lambda solution,_:     solution,            # not adding the input
        ],
        filter_functions = [
            lambda state,input: state+input<=capacity,    # adding the input
            lambda _,__:        True,                     # not adding the input
        ]
    ))
