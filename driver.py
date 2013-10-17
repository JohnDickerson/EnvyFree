#!/usr/bin/env python

from model import Model
import allocator
from allocator import DoesNotExistException
import time

def run(num_agents, num_items):

    # Randomly generate some data for N agents and M items
    m = Model.generate(num_agents, num_items)

    # Compute an envy-free allocation (if it exists)
    start = time.clock()
    sol_exists = True
    try:
        allocator.allocate(m)

    except DoesNotExistException:
        sol_exists = False

    stop = time.clock()
    sol_time = stop-start
    print "CPLEX allocator took {0:3f} seconds.".format(sol_time)
    
    return (sol_time, sol_exists)

if __name__ == '__main__':

    N = 1000
    sec_accum = 0.0
    sec_min = 10000.0
    sec_max = -1.0
    sol_exists_accum = 0
    for _ in xrange(N):
        
        # Generate an instance and solve it; returns runtime of IP write+solve
        secs, sol_exists = run(8,12)

        # Maintain stats on the runs
        sol_exists_accum += 1 if sol_exists else 0
        sec_accum += secs
        if secs < sec_min:
            sec_min = secs
        if secs > sec_max:
            sec_max = secs

    sec_avg = sec_accum / N
    print "Avg: {0:3f}, Min: {1:3f}, Max: {2:3f}".format(sec_avg, sec_min, sec_max)
    print "Fraction feasible: {0} / {1}".format(sol_exists_accum, N)
