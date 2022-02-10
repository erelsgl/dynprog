![Tox result](https://github.com/erelsgl/dynprog/workflows/tox/badge.svg)

# dynprog

Implements a generic routine for sequential dynamic programming, based on the "Simple DP" framework defined in:

> Gerhard J. Woeginger, [When Does a Dynamic Programming Formulation Guarantee the Existence of a FPTAS?](https://pubsonline.informs.org/doi/abs/10.1287/ijoc.12.1.57.11901), INFORMS journal of computing, 2000.

To define a dynamic program, extend the class `SequentialDynamicProgram` and override the methods:

* `initial_states` - returns a list of states where the search for a solution starts.
* `transition_functions` - returns a list of functions, each of which accepts a state and an input, and returns a new state.
* `filter_functions` - returns a list of functions, one for each transition function. Each of which accepts a state and an input, and returns `True` iff the transition is feasible.
* `value_function` - returns a function that accepts a state and returns its value (higher is better).

These functions are sufficient for computing the optimal (maximum) value, using the method `max_value`.

In order to also construct the optimal *solution*, you need to override two additional methods:

* `initial_solution` - returns an initial (usually empty) solution.
* `construction_functions` - returns a list of functions, one for each transition function. Each of which accepts a solution and an input, and returns a new solution.
 

## Example

Let us define a dynamic program for solving the Subset Sum problem.
Here, the state contains a single number: the sum of items in the subset.
Here is the class definition:

    from dynprog.sequential import SequentialDynamicProgram

    class SubsetSumDP(SequentialDynamicProgram):

        def __init__(self, capacity:int):
            self.capacity = capacity

        def initial_states(self):
            return [0]       # There is one initial state - 0.

        def initial_solution(self):
            return []        # There is one initial solution - an empty subset.

        def transition_functions(self):
            return  [        # There are two possible transitions from each state and input: 
                lambda state,input: state+input,    # adding the input
                lambda state,input: state+0,        # not adding the input
            ]

        def filter_functions(self):
            return [        # There are two corresponding filter functions:
                lambda state,input: state+input<=self.capacity,    # adding the input
                lambda _,__:        True,                          # not adding the input
            ]

        def construction_functions(self):
            return  [        # There are two possible construction functions: 
                lambda solution,input: solution+[input],    # adding the input
                lambda solution,_:     solution,            # not adding the input
            ]

        def value_function(self):      # The value of a state is just the state itself: 
            return lambda state: state

We can use it to compute the optimal value: 

    SubsetSumDP(capacity=4005).max_value(inputs=[100,200,400,700,1100,1600,2200,2900,3700])

or the optimal solution:

    SubsetSumDP(capacity=4005).max_value_solution(inputs=[100,200,400,700,1100,1600,2200,2900,3700])[2]


## More examples

More examples can be found in the examples folder:

* [Subset sum](examples/subset_sum.py)
* [Knapsack](examples/knapsack.py)
* [Longest palyndrome subsequence](examples/longest_palyndrome_subsequence.py)
* [Multiple subset sum](examples/multiple_subset_sum.py)
* [Best coin picking strategy](examples/best_coin_picking_strategy.py)



