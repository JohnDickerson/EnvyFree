#!/usr/bin/env python

from model import Model
import allocator
from allocator import DoesNotExistException

import time
import csv

def run(num_agents, num_items):

    # Randomly generate some data for N agents and M items
    #m = Model.generate_urand_int(num_agents, num_items)
    m = Model.generate_urand_real(num_agents, num_items)
    #m = Model.generate_zipf_real(num_agents, num_items, 2.)

    # Compute an envy-free allocation (if it exists)
    sol_exists, build_s, solve_s = allocator.allocate(m)
    
    return (sol_exists, build_s, solve_s)

if __name__ == '__main__':

    # Write one row per run, or one row per N runs (aggregate)?
    write_all = True

    with open('out.csv', 'wb') as csvfile:

        # Write overall stats to out.csv
        writer = csv.writer(csvfile, delimiter=',')

        for num_agents in range(10,26,5):
            
            # Phase transition plots runtime, %feas vs. #items
            for num_items in range(10,100,1):
                
                # Never feasible if fewer items than agents
                if num_items < num_agents:
                    continue

                N = 100
                build_s_accum = solve_s_accum = 0.0
                build_s_min = solve_s_min = 10000.0
                build_s_max = solve_s_max = -1.0
                sol_exists_accum = 0
                for _ in xrange(N):

                    # Generate an instance and solve it; returns runtime of IP write+solve
                    sol_exists, build_s, solve_s = run(num_agents, num_items)

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
                        writer.writerow([num_agents, num_items, N, sol_exists, build_s, solve_s])
                # Report stats over all N runs, both to stdout and to out.csv
                build_s_avg = build_s_accum / N
                solve_s_avg = solve_s_accum / N

                print "Build Avg: {0:3f}, Min: {1:3f}, Max: {2:3f}".format(build_s_avg, build_s_min, build_s_max)
                print "Solve Avg: {0:3f}, Min: {1:3f}, Max: {2:3f}".format(solve_s_avg, solve_s_min, solve_s_max)
                print "N={0}, M={1}, fraction feasible: {2} / {3}".format(num_agents, num_items, sol_exists_accum, N)

                # If we're only writing aggregate data, write that now
                if not write_all:
                    writer.writerow([num_agents, num_items, N, 
                                     sol_exists_accum, 
                                     build_s_avg, build_s_min, build_s_max,
                                     solve_s_avg, solve_s_min, solve_s_max,
                                     ])
                csvfile.flush()

