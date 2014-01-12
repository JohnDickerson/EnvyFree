#!/usr/bin/env python

from model import Model
from model import DupValues
from model import DistTypes
from model import ObjType
import allocator
import bounds
from allocator import DoesNotExistException
import argparse
import random

import time
import csv
import sys

current_ms_time = lambda: int(round(time.time() * 1000))

def run(num_agents, num_items, prefs, dup_values):

    # Randomly generate some data for N agents and M items
    if prefs.dist_type == DistTypes.urand_int:
        m = Model.generate_urand_int(num_agents, num_items, dup_values)
    elif prefs.dist_type == DistTypes.urand_real:
        m = Model.generate_urand_real(num_agents, num_items, dup_values)
    elif prefs.dist_type == DistTypes.zipf_real:
        m = Model.generate_zipf_real(num_agents, num_items, 2., dup_values)
    elif prefs.dist_type == DistTypes.polya_urn_real:
        m = Model.generate_polya_urn_real(num_agents, num_items, 2, 1)
    elif prefs.dist_type == DistTypes.correlated_real:
        m = Model.generate_correlated_real(num_agents, num_items)
    else:
        raise Exception("Distribution type {0} is not recognized.".format(dist_type))

    # Do our bounding at the root to check for naive infeasibility
    #is_possibly_feasible, bounding_s = bounds.max_contested_feasible(m)
    #if not is_possibly_feasible:
    #    print "Bounded infeasible!"
    #    sys.exit(-1)

    # Compute an envy-free allocation (if it exists)
    stats = allocator.allocate(m, prefs)
    
    return stats



def main():

    parser = argparse.ArgumentParser(description='Find envy-free allocations.')
    parser.add_argument("-f", "--filename", dest="filename", required=True,
                      metavar="FILE", help="write comma-delimited csv output to FILE")
    parser.add_argument("-r", "--num_repeats", type=int, dest="num_repeats", default=10,
                      metavar="R", help="num repeat runs per parameter setting")
    parser.add_argument("-n", type=int, nargs=3, dest="N", default=(5,6,1),
                      metavar=("N-min","N-max","stepsize"), help="range(a,b,c) iterating over num agents")
    parser.add_argument("-m", type=int, nargs=3, dest="M", default=(5,10,1),
                      metavar=("M-min","M-max","stepsize"), help="range(a,b,c) iterating over num items")
    parser.add_argument("--obj-feas", action="store_const", const=ObjType.feasibility, dest="obj_type",
                      help="Objective function: feasibility")
    parser.add_argument("--obj-social", action="store_const", const=ObjType.social_welfare_max, dest="obj_type",
                      help="Objective function: max social welfare")
    parser.add_argument("--dist-urand-int", action="store_const", const=DistTypes.urand_int, dest="dist_type",
                        help="Utility distribution integral in {0,...,10*#Items}")
    parser.add_argument("--dist-urand-real", action="store_const", const=DistTypes.urand_real, dest="dist_type",
                        help="Utility distribution u.a.r. real in U[0,1]")
    parser.add_argument("--dist-zipf-real", action="store_const", const=DistTypes.zipf_real, dest="dist_type",
                        help="Utility distribution drawn from Zipf with alpha=2.")
    parser.add_argument("--dist-polya-urn-real", action="store_const", const=DistTypes.polya_urn_real, dest="dist_type",
                        help="Utility distribution drawn from augmented Polya-Eggenberger urn model.")
    parser.add_argument("--dist-correlated-real", action="store_const", const=DistTypes.correlated_real, dest="dist_type",
                        help="Utility distribution correlated intrinsic item value.")
    parser.add_argument("-s", "--seed", type=long, dest="seed", default=0,
                        help="Sets the random seed in Python")
    parser.add_argument("--fathom-too-much-envy", action="store_true", dest="branch_fathom_too_much_envy", default=False,
                        help="Fathoms a path if #unallocated items is less than #envious agents at node")
    parser.add_argument("--branch-avg-value", action="store_true", dest="branch_avg_value", default=False,
                        help="Branching based on average item value and max agent value")
    parser.add_argument("--branch-sos1-envy", action="store_true", dest="branch_sos1_envy", default=False,
                        help="SOS1 branch to most envious agent [NOT IMPLEMENTED]")
    parser.add_argument("--prioritize-avg-value", action="store_true", dest="prioritize_avg_value", default=False,
                        help="Sets CPLEX branching priority based on average item value.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                        help="Prints a bunch of stats to stdout as we solve models.")
    parser.add_argument("-t", "--num-threads", type=int, default=1, dest="num_threads",
                        help="Sets the number of threads used by CPLEX.")
                      
    args = parser.parse_args()


    # If a random seed was explicitly passed in, set it
    if hasattr(args, "seed"):
        random.seed(args.seed)
    else:
        random.seed()

    # How to handle duplicate valuations for different items by the same agent?
    dup_values = DupValues.allowed

    # Write one row per run, or one row per N runs (aggregate)?
    write_all = True

    with open(args.filename, 'wb') as csvfile:

        # Write overall stats to out.csv
        writer = csv.writer(csvfile, delimiter=',')

        for num_agents in range(args.N[0], args.N[1], args.N[2]):

            # Phase transition plots runtime, %feas vs. #items
            for num_items in range(args.M[0], args.M[1], args.M[2]):
            
                # Never feasible if fewer items than agents
                if num_items < num_agents:
                    continue

                build_s_accum = solve_s_accum = 0.0
                build_s_min = solve_s_min = 10000.0
                build_s_max = solve_s_max = -1.0
                sol_exists_accum = 0
                for _ in xrange(args.num_repeats):

                    # Generate an instance and solve it; returns runtime of IP write+solve
                    stats = run(num_agents, num_items, args, dup_values)

                    sol_exists, build_s, solve_s = stats['ModelFeasible'], stats['ModelBuildTime'], stats['ModelSolveTime']

                    # Maintain stats on the runs
                    sol_exists_accum += 1 if sol_exists else 0
                    build_s_accum += build_s
                    solve_s_accum += solve_s
                    if build_s < build_s_min:
                        build_s_min = build_s
                    if solve_s < solve_s_min:
                        solve_s_min = solve_s
                    if build_s > build_s_max:
                        build_s_max = build_s
                    if solve_s > solve_s_max:
                        solve_s_max = solve_s

                    # If we're recording ALL data, write details for this one run
                    if write_all:
                        writer.writerow([args.seed, args.num_threads,
                                         num_agents, num_items, 
                                         args.dist_type, args.num_repeats, args.obj_type, 
                                         args.branch_fathom_too_much_envy, stats['MyTooMuchEnvyBranch'],
                                         args.branch_avg_value, stats['MyBranchOnAvgItemValue'],
                                         args.branch_sos1_envy, stats['MyBranchSOS1Envy'],
                                         args.prioritize_avg_value,
                                         sol_exists, stats['MIPNodeCount'], build_s, solve_s])
                        csvfile.flush()

                # Report stats over all N runs, both to stdout and to out.csv
                build_s_avg = build_s_accum / args.num_repeats
                solve_s_avg = solve_s_accum / args.num_repeats

                if args.verbose == True:
                    print "Build Avg: {0:3f}, Min: {1:3f}, Max: {2:3f}".format(build_s_avg, build_s_min, build_s_max)
                    print "Solve Avg: {0:3f}, Min: {1:3f}, Max: {2:3f}".format(solve_s_avg, solve_s_min, solve_s_max)
                    print "N={0}, M={1}, fraction feasible: {2} / {3}".format(num_agents, num_items, sol_exists_accum, args.num_repeats)

                # If we're only writing aggregate data, write that now
                if not write_all:
                    writer.writerow([args.seed, num_agents, num_items, 
                                     args.dist_type, args.num_repeats, args.obj_type, 
                                     args.branch_fathom_too_much_envy,
                                     args.branch_avg_value,
                                     sol_exists_accum, 
                                     build_s_avg, build_s_min, build_s_max,
                                     solve_s_avg, solve_s_min, solve_s_max,
                                     ])
                csvfile.flush()


if __name__ == '__main__':
    main()
