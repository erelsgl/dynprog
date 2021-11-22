"""
Generic dynamic programming in the iterative method.
Uses an abstract class interface.

-- NOT MAINTAINTED -- please use the function-based interface.

Programmer: Erel Segal-Halevi.
Since: 2021-11.
"""

from typing import *
from abc import ABC, abstractmethod
from numbers import Number

State = Any
Value = Number
StateValue = Tuple[State,Value]
StateValueData = Tuple[State,Value,Any]

import logging
logger = logging.getLogger(__name__)


class DynProg(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def initial_states(self)->Generator[StateValueData, None, None]:
        pass

    @abstractmethod
    def neighbors(self, state:State, value:Value, data:Any)->Generator[StateValueData, None, None]:
        pass

    def final_states(self)->Generator[State, None, None]:
        yield self.final_state

    def is_final_state(self, state:State)->bool:
        return state==self.final_state  # can be overridden to allow more than one final state


    def max_value(self):
        """
        This is a simple function that only returns the maximum value - it does not return the optimum solution.
        """
        open_states = []
        map_state_to_value = dict()
        for state_value_data in self.initial_states():
            (state,value,_) = state_value_data
            open_states.append(state)
            map_state_to_value[state]=value
        num_of_processed_states = 0
        while len(open_states)>0:
            current_state:State = open_states.pop(0)
            current_value = map_state_to_value[current_state]
            num_of_processed_states += 1
            logger.info("Opening state %s with value %s", current_state,current_value)
            for (next_state,next_value,_) in self.neighbors(current_state, current_value, None):
                if next_state in map_state_to_value: 
                    if next_value > map_state_to_value[next_state]:
                        map_state_to_value[next_state] = next_value
                        logger.info("Updating state %s to value %s", next_state,next_value)
                else:
                    open_states.append(next_state)
        logger.info("Processed %d states", num_of_processed_states)
        return max([map_state_to_value[state] for state in self.final_states()])


    def solve(self):
        open_states = []
        map_state_to_previous = dict()
        map_state_to_value = dict()
        for state_value_data in self.initial_states():
            open_states.append(state_value_data)
            (state,value,data) = state_value_data
            map_state_to_previous[state]=None
            map_state_to_value[state]=value

        reached_final_states = []
        num_of_processed_states = 0
        while True:
            if len(open_states)==0:
                logger.info("No more open states")
                break
            current_state_value_data:StateValueData = open_states.pop(0)
            num_of_processed_states += 1
            (current_state,current_value,current_data) = current_state_value_data
            logger.info("Opening state %s with value %s and data %s", current_state,current_value,current_data)
            if self.is_final_state(current_state):
                logger.info("State %s is final", current_state)
                reached_final_states.append(current_state_value_data)
            for next_state_value_data in self.neighbors(*current_state_value_data):
                (next_state,next_value,next_data) = next_state_value_data
                if next_state in map_state_to_previous: 
                    continue
                open_states.append(next_state_value_data)
                map_state_to_previous[next_state] = current_state_value_data

        logger.info("Processed %d states", num_of_processed_states)
        best_final_state_value_data = max(reached_final_states, key=lambda s: s[1])
        current_state_value_data = best_final_state_value_data
        path = []
        while True:
            logger.info("%s <-- ", current_state_value_data)
            (current_state,_,_) = current_state_value_data
            path.insert(0, current_state)
            previous = map_state_to_previous[current_state]
            if previous==None:
                logger.info("Start")
                break
            else:
                current_state_value_data = previous
        # logger.info("Path: %s", path)
        return best_final_state_value_data

    


DynProg.logger = logger



if __name__=="__main__":
    import sys
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

    # Example: longest palyndrome subsequence.
    class LPS(DynProg):
        def __init__(self,string):
            self.string = string
            self.lenstr = len(string)
            self.final_state = (0,self.lenstr)
        def initial_states(self):
            for i in range(self.lenstr): yield ((i,i+1),1, self.string[i])
            for i in range(self.lenstr): yield ((i,i),0, "")
        def neighbors (self, state:Tuple[int,int], value:int, data:str):
            (i,j) = state    # indices: represent the string between i and j-1.
            if i>0 and j<self.lenstr and self.string[i-1]==self.string[j]:  # add two letters to the palyndrome
                yield ((i-1,j+1),value+2,self.string[i-1]+data+self.string[j])
            else:    # add one letter in each side of the string, without extending the palyndrome
                if i>0:
                    yield ((i-1,j),value,data)  
                if j<self.lenstr:
                    yield ((i,j+1),value,data)

    print(LPS("a").max_value())
    print(LPS("bb").max_value())
    print(LPS("abcdba").max_value())

    # print(LPS("a").solve())
    print(LPS("bb").solve())
    # print(LPS("abcdba").solve())
