#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Raw .csv file containing data
filename_data = "../data/out.csv"

# Maps column indices to the data they hold
class Col:
    num_agents, num_items, dist_type, N, feasible, build_s, solve_s = range(7)

# Converts "True" or "False" to 1 or 0 integral, respectively
def get_boolean_from_string(s):
    s.strip
    if s.upper() == "TRUE" or s.upper() == "T":
        return 1.
    else:
        return 0.  # If we can't understand it, return false


# Load all the data at once
print 'Loading data from ' + filename_data
data = np.genfromtxt(filename_data, 
                    delimiter=',', 
                    skiprows=0,
                    converters={Col.feasible: get_boolean_from_string}, 
                    )
print 'Loaded ' + str(len(data)) + ' rows of data.'

# Grab proper iteration data
num_agents_list = np.unique(data[:,Col.num_agents])
num_items_list = np.unique(data[:,Col.num_items])

# Make the phase transition graphs
for num_agents in num_agents_list:

    data_num_agents = [row for row in data 
                       if row[Col.num_agents] == num_agents]
 
    # Want to plot (a) %feasible and (b) runtime to prove opt/infeas
    y_feas = []
    y_solve_s = []

    for num_items in num_items_list:
        
        # Grab just the data for this {number of agents, number of items}
        data_num_items = [row for row in data_num_agents 
                          if row[Col.num_items] == num_items]

        data_feas = np.array([row[Col.feasible] for row in data_num_items])
        data_solve_s = np.array([row[Col.solve_s] for row in data_num_items])

        y_feas.append( np.average(data_feas) )
        y_solve_s.appenD( np.average(data_solve_s) )

        
