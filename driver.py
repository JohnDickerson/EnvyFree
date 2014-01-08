#!/usr/bin/env python

from model import Model
from model import DupValues
from model import DistTypes
from model import ObjType
import allocator
import bounds
from allocator import DoesNotExistException
import argparse

import time
import csv
import sys

current_ms_time = lambda: int(round(time.time() * 1000))

def run(num_agents, num_items, dist_type, dup_values, obj_type):

    # Randomly generate some data for N agents and M items
    if dist_type == DistTypes.urand_int:
        m = Model.generate_urand_int(num_agents, num_items, dup_values)
    elif dist_type == DistTypes.urand_real:
        m = Model.generate_urand_real(num_agents, num_items, dup_values)
    elif dist_type == DistTypes.zipf_real:
        m = Model.generate_zipf_real(num_agents, num_items, 2., dup_values)
    elif dist_type == DistTypes.polya_urn_real:
        m = Model.generate_polya_urn_real(num_agents, num_items, 2, 1)
    elif dist_type == DistTypes.correlated_real:
        m = Model.generate_correlated_real(num_agents, num_items)
    else:
        raise Exception("Distribution type {0} is not recognized.".format(dist_type))

    m.obj_type = obj_type

    # Do our bounding at the root to check for naive infeasibility
    #is_possibly_feasible, bounding_s = bounds.max_contested_feasible(m)
    #if not is_possibly_feasible:
    #    print "Bounded infeasible!"
    #    sys.exit(-1)

    # Compute an envy-free allocation (if it exists)
    sol_exists, build_s, solve_s = allocator.allocate(m)
    
    return (sol_exists, build_s, solve_s)



def main():

    parser = argparse.ArgumentParser(description='Find envy-free allocations.')
    parser.add_argument("-f", "--filename", dest="filename", required=True,
                      metavar="FILE", help="write output to FILE")
    parser.add_argument("-r", "--num_repeats", type=int, dest="num_repeats", default=10,
                      help="num repeat runs per parameter setting")
    parser.add_argument("-n", type=int, nargs=3, dest="N", default=(5,6,1),
                      help="range(a,b,c) iterating over num agents")
    parser.add_argument("-m", type=int, nargs=3, dest="M", default=(5,10,1),
                      help="range(a,b,c) iterating over num items")
    parser.add_argument("--obj-feas", action="store_const", const=ObjType.feasibility, dest="obj_type",
                      help="Objective function: feasibility")
    parser.add_argument("--obj-social", action="store_const", const=ObjType.social_welfare_max, dest="obj_type",
                      help="Objective function: max social welfare")
    parser.add_argument("--dist-urand-int", action="store_const", const=DistTypes.urand_int, dest="dist_type")
    parser.add_argument("--dist-urand-real", action="store_const", const=DistTypes.urand_real, dest="dist_type")
    parser.add_argument("--dist-zipf-real", action="store_const", const=DistTypes.zipf_real, dest="dist_type")
    parser.add_argument("--dist-polya-urn-real", action="store_const", const=DistTypes.polya_urn_real, dest="dist_type")
    parser.add_argument("--dist-correlated-real", action="store_const", const=DistTypes.correlated_real, dest="dist_type")

    args = parser.parse_args()


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
                    sol_exists, build_s, solve_s = run(num_agents, num_items, args.dist_type, dup_values, args.obj_type)

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
                        writer.writerow([num_agents, num_items, args.dist_type, args.num_repeats, args.obj_type, sol_exists, build_s, solve_s])
                        csvfile.flush()

                # Report stats over all N runs, both to stdout and to out.csv
                build_s_avg = build_s_accum / args.num_repeats
                solve_s_avg = solve_s_accum / args.num_repeats

                print "Build Avg: {0:3f}, Min: {1:3f}, Max: {2:3f}".format(build_s_avg, build_s_min, build_s_max)
                print "Solve Avg: {0:3f}, Min: {1:3f}, Max: {2:3f}".format(solve_s_avg, solve_s_min, solve_s_max)
                print "N={0}, M={1}, fraction feasible: {2} / {3}".format(num_agents, num_items, sol_exists_accum, args.num_repeats)

                # If we're only writing aggregate data, write that now
                if not write_all:
                    writer.writerow([num_agents, num_items, 
                                     args.dist_type, args.num_repeats, args.obj_type,
                                     sol_exists_accum, 
                                     build_s_avg, build_s_min, build_s_max,
                                     solve_s_avg, solve_s_min, solve_s_max,
                                     ])
                csvfile.flush()


if __name__ == '__main__':
    main()
