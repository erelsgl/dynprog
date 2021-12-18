#!python3
"""
Common routines for dynamic programs finding fair allocations.
"""



def items_as_value_vectors(valuation_matrix):
    """
    Convert a valuation matrix (an input to a fair division algorithm) into a list of value-vectors.
    Each value-vector represents an item.
    """
    num_of_agents   = len(valuation_matrix)
    num_of_items    = len(valuation_matrix[0])
    return [  # Each item is represented by a vector of values - a value for each agent. The last value is the item index.
        [valuation_matrix[agent_index][item_index] for agent_index in range(num_of_agents)] + [item_index]
        for item_index in range(num_of_items)
    ]



def add_input_to_bin_sum(bin_sums:list, bin_index:int, input:int):
    """
    Adds the given input integer to bin #bin_index in the given list of bins.
    >>> add_input_to_bin_sum([11, 22, 33], 0, 77)
    (88, 22, 33)
    >>> add_input_to_bin_sum([11, 22, 33], 1, 77)
    (11, 99, 33)
    >>> add_input_to_bin_sum([11, 22, 33], 2, 77)
    (11, 22, 110)
    """
    new_bin_sums = list(bin_sums)
    new_bin_sums[bin_index] = new_bin_sums[bin_index] + input
    return tuple(new_bin_sums)


def add_input_to_agent_value(agent_values:list, agent_index:int, item_values:list):
    """
    Update the state of a dynamic program by giving an item to a specific agent.

    :param agent_values: the current vector of agent values, before adding the new item.
    :param agent_index: the agent to which the item is given.
    :param item_values: a list of values: input[i] represents the value of the current item for agent i.
    >>> add_input_to_agent_value([11, 22, 33], 0, [55,66,77,1])
    (66, 22, 33)
    >>> add_input_to_agent_value([11, 22, 33], 1, [55,66,77,1])
    (11, 88, 33)
    >>> add_input_to_agent_value([11, 22, 33], 2, [55,66,77,1])
    (11, 22, 110)
    """
    return add_input_to_bin_sum(agent_values, agent_index, item_values[agent_index])


def add_input_to_bin(bins:list, agent_index:int, item_index:int):
    """
    Update the solution of a dynamic program by giving an item to a specific agent.
    
    :param bins: the current vector of agent bundles, before adding the new item.
    :param agent_index: the agent to which the item is given.
    :param item_index: the index of the given item.

    Adds the given input integer to bin #agent_index in the given list of bins.
    >>> add_input_to_bin([[11,22], [33,44], [55,66]], 1, 1)
    [[11, 22], [33, 44, 1], [55, 66]]
    """
    new_bins = list(bins)
    new_bins[agent_index] = new_bins[agent_index]+[item_index]
    return new_bins





if __name__=="__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
