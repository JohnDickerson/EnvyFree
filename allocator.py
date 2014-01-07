import cplex
from cplex.exceptions import CplexError
from model import ObjType
import time
import sys

class DoesNotExistException(Exception):
    pass

def __flatten(list2d):
    """ Flattens a 2d list """
    return [val for val_list in list2d for val in val_list]

def __build_envyfree_problem(p, model):
   
    start = time.time()

    # Set objective function
    if model.obj_type == ObjType.social_welfare_max:
        # Objective: max \sum_i \sum_j v_{ij} x_{ij}
        p.objective.set_sense(p.objective.sense.maximize)
        obj = __flatten(model.u)
    elif model.obj_type == ObjType.feasibility:
        # Objective: nothing [just feasibility]
        obj = [0]*len(__flatten(model.u))
    else:
        print "Could not determine objective function type for model."
        sys.exit(-1)


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

    # Each item can be allocated to exactly one agent [SOS1]
    # For each item j, \sum_i x_{ij} = 1
    for j in xrange(model.m):
        rows.append([ [j + i*model.m for i in xrange(model.n)],
                      [1]*model.n
                      ])
        senses.append("E")
        rhs.append(1)

    # For each allocation A_i to agent i, and each allocation A_j to agent j,
    # make sure agent i values A_i at least as much as she values A_j
    for a_i in xrange(model.n):

        # Add A_i's valuation for her allocation 
        i_indices = [a_i*model.m + j for j in xrange(model.m)]
        i_values = model.u[a_i]

        for a_j in xrange(model.n):

            # Agent i is not envious of her own allocation
            if a_i == a_j:
                continue
        
            # Subtract off A_i's value for each of A_j's allocated items
            j_indices = [a_j*model.m + j for j in xrange(model.m)]
            j_values = [ -1*val for val in model.u[a_i] ]

            rows.append([ i_indices + j_indices,
                          i_values + j_values
                          ])
            senses.append("G")
            rhs.append(0)

    p.linear_constraints.add(lin_expr = rows,
                             rhs = rhs, 
                             senses = senses,
                             )

    stop = time.time()
    return stop-start


def allocate(model):

    try:
        # Build the envy-free IP
        p = cplex.Cplex()
        p.set_results_stream(None)
        build_s = __build_envyfree_problem(p, model)

        # Solve the IP
        start = time.time()
        p.solve()
        stop = time.time()
        solve_s = stop - start

        # Was there a solution? (not guaranteed for envy-free)
        feasible = True
        sol = p.solution
        if sol.get_status() == 3 or sol.get_status() == 103:
            feasible = False
        else:
            print "{0:d}:  {1}   ||   Objective value: {2:2f}".format(
                sol.get_status(), 
                sol.status[sol.get_status()], 
                sol.get_objective_value())

        # Keep stats on feasibility, time
        return (feasible, build_s, solve_s)
        
    except CplexError, ex:
        print ex
        sys.exit(-1)

