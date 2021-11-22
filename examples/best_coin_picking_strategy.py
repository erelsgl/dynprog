#!python3
"""
Uses the generic dynamic programming function to compute an optimal strategy
in a game of picking coins from a row.

See here: https://www.youtube.com/watch?v=Tw1k46ywN6E, time 54:30

The states are tuples (i,j,b), where i,j are indices and b is boolean.
Each pair (i,j) represents the optimal strategy for picking from the sequence i, ..., j-1.
The boolean value b is "True" if it is my turn, "False" if it is the opponent's turn.

Programmer: Erel Segal-Halevi
Since: 2021-11
"""

import dynprog
from typing import *
from numbers import Number


def max_value(coins: List[Number], first:bool):
    """
    Returns the maximum value that the player can win from the given sequence of coins.
    `first` is true iff the current player plays first.

    >>> max_value([1,2,3,4], True)
    6
    >>> max_value([6,5,4,3,2], True)
    12
    >>> max_value([1,2,3,4], False)
    4
    >>> max_value([6,5,4,3,2], False)
    8
    """
    num_coins = len(coins)
    def initial_states():  # returns (state,value) tuples
        for i in range(num_coins): yield ((i,i,first if num_coins%2==0 else not first), 0)
    def neighbors (state:Tuple[int,int], value:int):   # returns (state,value) tuples
        (i,j,my_turn) = state    # indices: represent the row of coins between i and j-1.
        if my_turn:
            if i-1>=0:   # check the state (i-1,j)
                yield ((i-1,j,False), -value)
            if j+1<=num_coins:
                yield ((i,j+1,False), -value)
        else:
            if i-1>=0:   # check the state (i-1,j)
                yield ((i-1,j,True), -value + coins[i-1])
            if j+1<=num_coins:
                yield ((i,j+1,True), -value + coins[j])
    def final_states():
        yield (0,num_coins,first)
    value = dynprog.max_value(initial_states=initial_states, neighbors=neighbors, final_states=final_states)
    return value if first else -value

# def max_value_solution(string:str,count_states=False):
#     """
#     Finds the longest palyndromic subsequence in the given string.

#     >>> LPS_string("a")
#     'a'
#     >>> LPS_string("bb")
#     'bb'
#     >>> LPS_string("abcdba")
#     'abcba'
#     >>> LPS_string("programming")
#     'gmmg'
#     """
#     lenstr = len(string)
#     def initial_states():  # returns (state,value,data) tuples
#         for i in range(lenstr): yield ((i,i+1),1,string[i])
#         for i in range(lenstr): yield ((i,i),0,"")
#     def neighbors (state:Tuple[int,int], value:int, data:str): # returns (state,value,data) tuples
#         (i,j) = state    # indices: represent the string between i and j-1.
#         if i>0 and j<lenstr and string[i-1]==string[j]:  # add two letters to the palyndrome
#             yield ((i-1,j+1),value+2,string[i-1]+data+string[j])
#         else:    # add one letter in each side of the string, without extending the palyndrome
#             if i>0:  yield ((i-1,j),value,data)
#             if j<lenstr:  yield ((i,j+1),value,data)
#     def final_states():
#         yield (0,lenstr)
#     (state, value, data, num_of_states) = dynprog.max_value_solution(initial_states=initial_states, neighbors=neighbors, final_states=final_states)
#     return (state,value,data,num_of_states) if count_states else data


if __name__=="__main__":
    import sys, logging
    dynprog.logger.addHandler(logging.StreamHandler(sys.stdout))
    # dynprog.logger.setLevel(logging.INFO)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
