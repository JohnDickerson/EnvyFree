#!/usr/bin/env python

from model import Model
import allocator
from allocator import DoesNotExistException
import time

def run():

    # Randomly generate some data for N agents and M items
    m = Model.generate(5,5)

    # Compute an envy-free allocation (if it exists)
    start = time.clock()
    try:
        allocator.allocate(m)

    except DoesNotExistException:
        print "No envy-free allocation exists!"
    

    stop = time.clock()
    print "CPLEX allocator took {0:3f} seconds.".format(stop-start)

if __name__ == '__main__':
    run()
