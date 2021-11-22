#!python3
"""
Uses the generic dynamic programming function to solve the
Longest Palyndrome Subsequence problem.

The states are pairs (i,j), where i,j are indices. 
Each pair (i,j) represents the longest palyndromic subsequence in the substring i, i+1, ..., j-1.

Programmer: Erel Segal-Halevi
Since: 2021-11
"""

import dynprog
from typing import *


def max_value(string:str):
    """
    Returns the length of the longest palyndromic subsequence in the given string.
    Does *not* return the string itself - see below.

    >>> dynprog.logger.setLevel(logging.WARNING)
    >>> max_value("a")
    1
    >>> dynprog.logger.setLevel(logging.WARNING)
    >>> max_value("bb")
    2
    >>> dynprog.logger.setLevel(logging.WARNING)
    >>> max_value("abcdba")
    5
    >>> max_value("programming")
    4
    """
    lenstr = len(string)
    def initial_states():  # returns (state,value) tuples
        for i in range(lenstr): yield ((i,i+1),1)
        for i in range(lenstr): yield ((i,i),0)
    def neighbors (state:Tuple[int,int], value:int):   # returns (state,value) tuples
        (i,j) = state    # indices: represent the string between i and j-1.
        if i>0 and j<lenstr and string[i-1]==string[j]:  # add two letters to the palyndrome
            yield ((i-1,j+1),value+2)
        else:    # add one letter in each side of the string, without extending the palyndrome
            if i>0:      yield ((i-1,j),value)  
            if j<lenstr: yield ((i,j+1),value)
    def final_states():
        yield (0,lenstr)
    return dynprog.max_value(initial_states=initial_states, neighbors=neighbors, final_states=final_states)

def max_value_solution(string:str,count_states=False):
    """
    Finds the longest palyndromic subsequence in the given string.

    >>> dynprog.logger.setLevel(logging.WARNING)
    >>> max_value_solution("a")
    'a'
    >>> max_value_solution("bb")
    'bb'
    >>> max_value_solution("abcdba")
    'abcba'
    >>> max_value_solution("programming")
    'gmmg'
    """
    lenstr = len(string)
    def initial_states():  # returns (state,value,data) tuples
        for i in range(lenstr): yield ((i,i+1),1,string[i])
        for i in range(lenstr): yield ((i,i),0,"")
    def neighbors (state:Tuple[int,int], value:int, data:str): # returns (state,value,data) tuples
        (i,j) = state    # indices: represent the string between i and j-1.
        if i>0 and j<lenstr and string[i-1]==string[j]:  # add two letters to the palyndrome
            yield ((i-1,j+1),value+2,string[i-1]+data+string[j])
        else:    # add one letter in each side of the string, without extending the palyndrome
            if i>0:  yield ((i-1,j),value,data)
            if j<lenstr:  yield ((i,j+1),value,data)
    def final_states():
        yield (0,lenstr)
    (state, value, data, num_of_states) = dynprog.max_value_solution(initial_states=initial_states, neighbors=neighbors, final_states=final_states)
    return (state,value,data,num_of_states) if count_states else data


if __name__=="__main__":
    import sys, logging
    dynprog.logger.addHandler(logging.StreamHandler(sys.stdout))

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))

    print(max_value("programming"))
    print(max_value_solution("programming"))
    print(max_value_solution("programming", count_states=True))
