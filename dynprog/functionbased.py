"""
Generic dynamic programming in the iterative method.
Uses a function interface.

Programmer: Erel Segal-Halevi.
Since: 2021-11.
"""

from typing import *
from numbers import Number

State = Any
Value = Number
StateValue = Tuple[State,Value]
StateValueData = Tuple[State,Value,Any]

import logging
logger = logging.getLogger(__name__)


def max_value(
    initial_states: Generator[StateValue, None, None], 
    neighbors:      Callable[[StateValue], Generator[StateValue, None, None]],
    final_states:   Generator[State, None, None], 
    ):
    """
    This is a simple function that only returns the maximum value - it does not return the optimum solution.
    """
    open_states = []
    map_state_to_value = dict()
    for state,value in initial_states():
        open_states.append(state)
        map_state_to_value[state]=value
    num_of_processed_states = 0
    while len(open_states)>0:
        current_state:State = open_states.pop(0)
        current_value = map_state_to_value[current_state]
        logger.info("Processing state %s with value %s", current_state,current_value)
        num_of_processed_states += 1
        for (next_state,next_value) in neighbors(current_state, current_value):
            if next_state in map_state_to_value: 
                map_state_to_value[next_state] = max(map_state_to_value[next_state], next_value)
            else:
                map_state_to_value[next_state] = next_value
                open_states.append(next_state)
    logger.info("Processed %d states", num_of_processed_states)
    return max([map_state_to_value[state] for state in final_states()])



def max_value_solution(
    initial_states: Generator[StateValueData, None, None], 
    neighbors:      Callable[[StateValueData], Generator[StateValueData, None, None]],
    final_states:   Generator[State, None, None], 
    ):
    """
    This function returns both the maximum value and the corresponding optimum solution.
    """
    open_states = []
    map_state_to_value = dict()
    map_state_to_data = dict()
    for state,value,data in initial_states():
        open_states.append(state)
        map_state_to_value[state]=value
        map_state_to_data[state]=data
    num_of_processed_states = 0
    while len(open_states)>0:
        current_state:State = open_states.pop(0)
        current_value = map_state_to_value[current_state]
        current_data  = map_state_to_data[current_state]
        num_of_processed_states += 1
        logger.info("Processing state %s with value %s and data %s", current_state,current_value,current_data)
        for (next_state,next_value,next_data) in neighbors(current_state, current_value, current_data):
            if next_state in map_state_to_value: 
                if next_value > map_state_to_value[next_state]:
                    logger.info("Improving state %s to value %s and data %s", next_state,next_value,next_data)
                    map_state_to_value[next_state] = next_value
                    map_state_to_data[next_state]  = next_data
                pass
            else:
                map_state_to_value[next_state] = next_value
                map_state_to_data[next_state] = next_data
                open_states.append(next_state)
    logger.info("Processed %d states", num_of_processed_states)
    best_final_state = max(list(final_states()), key=lambda state:map_state_to_value[state])
    return (
        best_final_state, 
        map_state_to_value[best_final_state], 
        map_state_to_data[best_final_state],
        num_of_processed_states)



if __name__=="__main__":
    import sys
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

    # Example: longest palyndrome subsequence.
    string = "abcdba"
    lenstr = len(string)
    def initial_states_short():  # only state and value
        for i in range(lenstr): yield ((i,i+1),1)
        for i in range(lenstr): yield ((i,i),0)
    def initial_states_long():   # state value and data
        for i in range(lenstr): yield ((i,i+1),1, string[i])
        for i in range(lenstr): yield ((i,i),0, "")
    def neighbors_short(state:Tuple[int,int], value:int):    # only state and value
        (i,j) = state    # indices: represent the string between i and j-1.
        if i>0 and j<lenstr and string[i-1]==string[j]:  # add two letters to the palyndrome
            yield ((i-1,j+1),value+2)
        else:    # add one letter in each side of the string, without extending the palyndrome
            if i>0:
                yield ((i-1,j),value)  
            if j<lenstr:
                yield ((i,j+1),value)
    def neighbors_long(state:Tuple[int,int], value:int, data:str):   # state and value and data
        (i,j) = state    # indices: represent the string between i and j-1.
        if i>0 and j<lenstr and string[i-1]==string[j]:  # add two letters to the palyndrome
            yield ((i-1,j+1),value+2,string[i-1]+data+string[j])
        else:    # add one letter in each side of the string, without extending the palyndrome
            if i>0:
                yield ((i-1,j),value,data)  
            if j<lenstr:
                yield ((i,j+1),value,data)
    def final_states():
        yield (0, lenstr)

    print(max_value(initial_states=initial_states_short,neighbors=neighbors_short,final_states=final_states))
    print(max_value_solution(initial_states=initial_states_long,neighbors=neighbors_long,final_states=final_states))
