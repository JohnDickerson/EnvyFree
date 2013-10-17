import cplex
from cplex.exceptions import CplexError

class DoesNotExistException(Exception):
    pass

def __flatten(list2d):
    """ Flattens a 2d list """
    return [val for val_list in list2d for val in val_list]

def __build_envyfree_problem(p, model):
    
    #
    # Objective: max \sum_i \sum_j v_{ij} x_{ij}
    p.objective.set_sense(p.objective.sense.maximize)
    obj = __flatten(model.u)

    # One binary variable per item per agent
    lb = [0]*len(obj)
    ub = [1]*len(obj)
    types = "I"*len(obj)

    p.variables.add(obj = obj,
                    lb = lb,
                    ub = ub,
                    types = types,
                    )

    
    #
    # Now build the constraint matrix (incrementally)
    rows = []
    senses = []
    rhs = []

    # Each item can be allocated to at most one agent [SOS1]
    # For each item j, \sum_i x_{ij} \leq 1
    for j in xrange(model.m):
        indices = []
        values = []
        for i in xrange(model.n):
            indices.append(j + i*model.n)
            values.append(1)
        rows.append([indices, values])
        senses.append("L")
        rhs.append(1)

    # For each allocation to agent i, make sure 



    

    p.linear_constraints.add(lin_expr = rows,
                             rhs = rhs, 
                             senses = senses,
                             )



def allocate(model):

    try:
        # Build the envy-free IP
        p = cplex.Cplex()
        __build_envyfree_problem(p, model)

        # Was there a solution? (not guaranteed for envy-free)
        sol = p.solution
        print sol.get_status()
        print sol.status[sol.get_status()]

    except CplexError, ex:
        print ex
        return 


