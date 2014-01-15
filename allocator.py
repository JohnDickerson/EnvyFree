import cplex
from cplex.exceptions import CplexError
from model import ObjType
import time
import sys
from ef_callbacks import MyTooMuchEnvyBranch, MyBranchOnAvgItemValue, MyMIPInfo, MyTooMuchEnvyAndBranchOnAvgItemValue, MyTooMuchEnvyAndBranchSOS1Envy


class DoesNotExistException(Exception):
    pass

def __flatten(list2d):
    """ Flattens a 2d list """
    return [val for val_list in list2d for val in val_list]

def __build_envyfree_problem(p, model, prefs):
   
    start = time.time()
    
    # Set objective function
    if prefs.obj_type == ObjType.social_welfare_max:
        # Objective: max \sum_i \sum_j v_{ij} x_{ij}
        p.objective.set_sense(p.objective.sense.maximize)
        obj = __flatten(model.u)
    elif prefs.obj_type == ObjType.feasibility:
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



# Essentially the same IP as __build_envyfree_problem, but with
# a single additional variable representing the max envy between
# any two pair of agents
def __build_envyfree_problem_alt(p, model, prefs):
   
    start = time.time()

    # Set objective function
    # Objective: 0*[binary allocation variables] + 1*[envy variable]
    p.objective.set_sense(p.objective.sense.minimize)
    obj = [0]*len(__flatten(model.u)) + [1]

    
    # One binary variable per item per agent, and one continuous variable
    # representing the maximum envy between pairs of agents
    lb = [0]*(len(obj)-1) + [0]
    ub = [1]*(len(obj)-1) + [cplex.infinity]
    types = "I"*(len(obj)-1) + "C"

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
    E_idx = len(obj)-1   # E variable is the last column
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

            rows.append([ i_indices + j_indices + [E_idx],
                          i_values + j_values + [1.0]
                          ])
            
            # {my val, my bundle} - {my val, your bundle} + E >= 0
            # For envy-free, sets E = 0 via minimization of objective
            senses.append("G")
            rhs.append(0)

    p.linear_constraints.add(lin_expr = rows,
                             rhs = rhs, 
                             senses = senses,
                             )

    stop = time.time()
    return stop-start




def allocate(model, prefs):

    try:
        # Record any runtime, build statistics from solving the model
        stats = {'MyTooMuchEnvyBranch':0, 'MyBranchOnAvgItemValue':0, 'MyBranchSOS1Envy':0}

        # Keep CPLEX quiet, if requested
        p = cplex.Cplex()
        p.set_results_stream(None)
        if prefs.verbose == False:
            p.parameters.mip.display.set(0)

        # CPLEX global parameters 
        p.parameters.threads.set(prefs.num_threads)
        p.parameters.simplex.tolerances.feasibility.set(1e-9)

        #
        # Build the envy-free IP (either of two models
        if prefs.alternate_IP_model:
            build_s = __build_envyfree_problem_alt(p, model, prefs)
        else:
            build_s = __build_envyfree_problem(p, model, prefs)
        stats['ModelBuildTime'] = build_s

        # Register any special branching rules
        # Must disable CPLEX dynamic search if we have any branching rules
        if prefs.branch_fathom_too_much_envy or prefs.branch_avg_value or prefs.branch_sos1_envy:
            p.parameters.mip.strategy.search.set(p.parameters.mip.strategy.search.values.traditional)

        # Can have (TooMuchEnvy fathoming + at most 1 other branching rule)
        if prefs.branch_fathom_too_much_envy:
            if prefs.branch_avg_value:
                my_too_much_envy_and_branch_avg_item = p.register_callback(MyTooMuchEnvyAndBranchOnAvgItemValue)
                my_too_much_envy_and_branch_avg_item.times_too_much_envy_used = 0
                my_too_much_envy_and_branch_avg_item.times_branch_on_avg_item_used = 0
                my_too_much_envy_and_branch_avg_item.model = model
            elif prefs.branch_sos1_envy:
                my_too_much_envy_and_branch_sos1_envy = p.register_callback(MyTooMuchEnvyAndBranchSOS1Envy)
                my_too_much_envy_and_branch_sos1_envy.times_too_much_envy_used = 0
                my_too_much_envy_and_branch_sos1_envy.times_sos1_envy_used = 0
                my_too_much_envy_and_branch_sos1_envy.model = model
            else:      
                my_too_much_envy = p.register_callback(MyTooMuchEnvyBranch)
                my_too_much_envy.times_used = 0
                my_too_much_envy.model = model
        elif prefs.branch_avg_value:
            my_branch_avg_item = p.register_callback(MyBranchOnAvgItemValue)
            my_branch_avg_item.times_used = 0
            my_branch_avg_item.model = model
        elif prefs.branch_sos1_envy:
            my_branch_sos1_envy = p.register_callback(MyBranchSOS1Envy)
            my_branch_sos1_envy.times_used = 0
            my_branch_sos1_envy.model = model

        # Keep track of B&C tree information via MIPInfoCallback
        my_mip_info = p.register_callback(MyMIPInfo)
        my_mip_info.num_nodes = 0 

        # Possibly prioritize variables based on their average value (value \propto priority)
        if prefs.prioritize_avg_value:
            
            item_positions = sorted(range(model.m), key=lambda k: model.m_avg_vals[k])
            item_priorities = []
            for item_idx, position in enumerate(item_positions):
                # Priority: lowest is 1 (M - last in sorted list), highest is M (M - first=0)
                priority = model.m - position
                # Set priorities for each of the binary variables for this item
                for agent_idx in xrange(model.n):
                    # order must be a list of triples (variable, priority, direction)
                    bin_var_idx = (agent_idx * model.m) + item_idx
                    item_priorities.append( (bin_var_idx, priority, p.order.branch_direction.up) )
            
            p.order.set(item_priorities)


            
        #
        # Solve the IP
        start = time.time()
        p.solve()
        stop = time.time()
        solve_s = stop - start
        stats['ModelSolveTime'] = solve_s
        stats['MIPNodeCount'] = my_mip_info.num_nodes

        #
        # Record stats from the run
        if prefs.branch_fathom_too_much_envy:
            if prefs.branch_avg_value:
                stats['MyTooMuchEnvyBranch'] = my_too_much_envy_and_branch_avg_item.times_too_much_envy_used
                stats['MyBranchOnAvgItemValue'] = my_too_much_envy_and_branch_avg_item.times_branch_on_avg_item_used
            elif prefs.branch_sos1_envy:
                stats['MyTooMuchEnvyBranch'] = my_too_much_envy_and_branch_sos1_envy.times_too_much_envy_used
                stats['MyBranchSOS1Envy'] = my_too_much_envy_and_branch_sos1_envy.times_sos1_envy_used
            else:
                stats['MyTooMuchEnvyBranch'] = my_too_much_envy.times_used
        elif prefs.branch_avg_value:
            stats['MyBranchOnAvgItemValue'] = my_branch_avg_item.times_used
        elif prefs.branch_sos1_envy:
            stats['MyBranchSOS1Envy'] = my_branch_sos1_envy.times_used


        # Was there a solution? (not guaranteed for envy-free)
        feasible = True
        sol = p.solution

        if sol.get_status() == 3 or sol.get_status() == 103:
            feasible = False
            stats['MIPObjVal'] = 0
        else:
            # If we're using the second IP, E-F exists if objective <= 0
            # check if the obj is >0 (plus CPLEX's default constraint violation error)
            if prefs.alternate_IP_model and sol.get_objective_value() > 1e-6:
                feasible = False
            stats['MIPObjVal'] = sol.get_objective_value()
            
            if feasible == True:
                if prefs.verbose:
                    print "{0:d}:  {1}   ||   Objective value: {2:2f}".format(
                        sol.get_status(), 
                        sol.status[sol.get_status()], 
                        sol.get_objective_value())
                    
        stats['ModelFeasible'] = feasible

        # Keep stats on feasibility, time
        return stats
        
    except CplexError, ex:
        print ex
        sys.exit(-1)

