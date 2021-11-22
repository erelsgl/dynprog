#!python3

import dynprog
from typing import *


def max_value(string:str):
    """
    Returns the length of the longest palyndromic subsequence in the given string.
    Does *not* return the string itself - see below.

    >>> import sys, logging
    >>> #dynprog.logger.addHandler(logging.StreamHandler(sys.stdout))

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
    def initial_states():  # only state and value
        for i in range(lenstr): yield ((i,i+1),1)
        for i in range(lenstr): yield ((i,i),0)
    def neighbors (state:Tuple[int,int], value:int):   # return only state and value
        (i,j) = state    # indices: represent the string between i and j-1.
        if i>0 and j<lenstr and string[i-1]==string[j]:  # add two letters to the palyndrome
            yield ((i-1,j+1),value+2)
        else:    # add one letter in each side of the string, without extending the palyndrome
            if i>0:
                yield ((i-1,j),value)  
            if j<lenstr:
                yield ((i,j+1),value)
    def final_states():
        yield (0,lenstr)
    return dynprog.max_value(initial_states=initial_states, neighbors=neighbors, final_states=final_states)

def max_value_solution(string:str):
    """
    Finds the longest palyndromic subsequence in the given string.

    >>> import sys, logging
    >>> dynprog.logger.addHandler(logging.StreamHandler(sys.stdout))

    >>> dynprog.logger.setLevel(logging.WARNING)
    >>> max_value_solution("a")
    (1, 'a')
    >>> max_value_solution("bb")
    (2, 'bb')
    >>> max_value_solution("abcdba")
    (5, 'abcba')
    >>> max_value_solution("programming")
    (4, 'gmmg')
    """
    lenstr = len(string)
    def initial_states():  # only state and value
        for i in range(lenstr): yield ((i,i+1),1,string[i])
        for i in range(lenstr): yield ((i,i),0,"")
    def neighbors (state:Tuple[int,int], value:int, data:str):
        (i,j) = state    # indices: represent the string between i and j-1.
        if i>0 and j<lenstr and string[i-1]==string[j]:  # add two letters to the palyndrome
            yield ((i-1,j+1),value+2,string[i-1]+data+string[j])
        else:    # add one letter in each side of the string, without extending the palyndrome
            if i>0:
                yield ((i-1,j),value,data)
            if j<lenstr:
                yield ((i,j+1),value,data)
    def final_states():
        yield (0,lenstr)
    (state, value, data) = dynprog.max_value_solution(initial_states=initial_states, neighbors=neighbors, final_states=final_states)
    return (value, data)
    

if __name__=="__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
