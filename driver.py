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
    try:
        allocator.allocate(m)

    except DoesNotExistException:
        print "No envy-free allocation exists!"
    

    stop = time.clock()
    print "CPLEX allocator took {0:3f} seconds.".format(stop-start)
    return (stop-start)

if __name__ == '__main__':

    N = 1000
    sec_accum = 0.0
    sec_min = 10000.0
    sec_max = -1.0
    for _ in xrange(10000):
        
        # Generate an instance and solve it; returns runtime of IP write+solve
        secs = run(8,25)

        # Maintain stats on the runs
        sec_accum += secs
        if secs < sec_min:
            sec_min = secs
        if secs > sec_max:
            sec_max = secs

    sec_avg = sec_accum / N
    print "Avg: {0:3f}, Min: {0:3f}, Max: {0:3f}".format(sec_avg, sec_min, sec_max)
