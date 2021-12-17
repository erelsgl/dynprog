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
Solution = Any

import logging
logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod

class SequentialDynamicProgram(ABC):

    ### The following abstract methods define the dynamic program.
    ### You should override them for each specific problem.

    @abstractmethod   # Return a set of initial states [The set S_0 in the paper].
    def initial_states(self)->Set[State]:  
        return {0} 

    @abstractmethod   # Return a list of functions; each function maps a pair (state,input) to a new state [The set F in the paper].
    def transition_functions(self)->List[Callable[[State, Input], State]]: 
        return [lambda state,input: state]

    @abstractmethod   # Return a function that maps a state to its "value" (that should be maximized). [The function g in the paper].
    def value_function(self)->Callable[[State], Value]:
        return lambda state:0

    # Return a set of functions; each function maps a pair (state,input) to a boolean value which is "true" iff the new state should be added [The set H from the paper].
    # By default, there is no filtering - every state is legal.
    def filter_functions(self)->List[Callable[[State, Input], bool]]: 
        return [(lambda state,input: True) for _ in self.transition_functions()]
    
    @abstractmethod   
    def initial_solution(self)->Solution:
        return []

    @abstractmethod   
    def construction_functions(self) -> List[Callable[[Solution, Input], Solution]]:
        return [(lambda solution,input: solution) for _ in self.transition_functions()]

    def max_value(self, inputs:List[Input]):
        """
        This function that only returns the maximum value - it does not return the optimum solution.
        :param inputs: the list of inputs.
        """
        current_states = set(self.initial_states())
        transition_functions = self.transition_functions()
        filter_functions = self.filter_functions()
        value_function = self.value_function()
        logger.info("%d initial states, %d transition functions, %d filter functions.", len(current_states), len(transition_functions), len(filter_functions))
        num_of_processed_states = len(current_states)
        for input_index,input in enumerate(inputs):
            next_states = {
                f(state,input)
                for (f,h) in zip(transition_functions,filter_functions)
                for state in current_states
                if h(state,input)
            }
            # logger.info("Processed input %d (%s) and added %d states: %s.", input_index, input, len(next_states), next_states)
            logger.info("  Processed input %d (%s) and added %d states.", input_index, input, len(next_states))
            num_of_processed_states += len(next_states)
            current_states = next_states
        logger.info("Processed %d states.", num_of_processed_states)
        if len(current_states)==0:
            raise ValueError("No final states!")
        return max([value_function(state) for state in current_states])



    def max_value_solution(self, inputs: List[Input]):
        """
        This function returns both the maximum value and the corresponding optimum solution.
        :param inputs: the list of inputs.
        """
        inputs = list(inputs)  # allow to iterate twice. See https://stackoverflow.com/q/70381559/827927

        @dataclass
        class StateRecord:
            state: State
            prev:  Any #StateRecord
            transition_index: int  # the index of the transition function used to go from prev to state.
            def __hash__(self):
                return hash(self.state)
            def __eq__(self,other):
                return (self.state==other.state)


        current_state_records = {StateRecord(state,None,None) for state in self.initial_states()} # Add a link to the 'previous state', which is initially None.
        transition_functions = self.transition_functions()
        filter_functions = self.filter_functions()
        value_function = self.value_function()
        construction_functions = self.construction_functions()
        logger.info("%d initial states, %d transition functions, %d filter functions, %d construction functions.", len(current_state_records), len(transition_functions), len(filter_functions), len(construction_functions))
        num_of_processed_states = len(current_state_records)
        for input_index,input in enumerate(inputs):
            next_state_records = {
                StateRecord(f(record.state,input), record, transition_index)
                for (transition_index,(f,h)) in enumerate(zip(transition_functions,filter_functions))
                for record in current_state_records
                if h(record.state, input)
            }
            logger.info("  Processed input %d (%s) and added %d states.", input_index, input, len(next_state_records))
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
        solution = self.initial_solution()
        for input_index,input in enumerate(inputs):
            transition_index = path[input_index]
            logger.info("  Input %d (%s): transition %d", input_index, input, transition_index)
            solution = construction_functions[transition_index](solution, input)
        
        return (best_final_state, best_final_state_value, solution, num_of_processed_states)



if __name__=="__main__":
    import sys
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

    # Example: subset sum with fixed capacity.
    capacity = 4005
    class SubsetSumDP(SequentialDynamicProgram):
        def initial_states(self):
            return {0}
        def transition_functions(self):
            return [
                lambda state,input: state+input,    # adding the input
                lambda state,_:     state+0,        # not adding the input
            ]
        def value_function(self):
            return lambda state: state
        def initial_solution(self):
            return []
        def construction_functions(self):
            return [
                lambda solution,input: solution+[input],    # adding the input
                lambda solution,_:     solution,            # not adding the input
            ]
        def filter_functions(self):
            return [
                lambda state,input: state+input<=capacity,    # adding the input
                lambda _,__:        True,                     # not adding the input
            ]

    inputs = [100,200,300,400,700,1100,1600,2200,2900,3700]

    ssdp = SubsetSumDP()
    print(ssdp.max_value(inputs))
    print(ssdp.max_value_solution(inputs))
