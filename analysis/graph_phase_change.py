#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches   # For the proxy twin-axis legend entry

# Raw .csv file containing data
filename_data = "../data/out.csv"

# Maps column indices to the data they hold
class Col:
    num_agents, num_items, dist_type, N, feasible, build_s, solve_s = range(7)

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

XFONT={'fontsize':24}
YFONT={'fontsize':24}
TITLEFONT={'fontsize':24}
TINYFONT={'fontsize':6}

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
        y_solve_s.append( np.average(data_solve_s) )

    # Plot both lines (%feas and runtime) on same x-axis, with two y-axes
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plot_feas = ax.plot(num_items_list, y_feas,
                        color='crimson',
                        )
    proxy_feas = matplotlib.patches.Rectangle((0,0), width=1, height=0.1, facecolor='crimson')

    # Fraction feasible is in [0,1]
    plt.ylim(0.0, 1.0)
    ax.set_xscale('log')
    
    ax2 = ax.twinx()
    plot_solve = ax2.plot(num_items_list, y_solve_s,
                          color='black',
                          )
    proxy_solve = matplotlib.patches.Rectangle((0,0), width=1, height=0.1, facecolor='black')

    # Prettify the plot
    ax.set_title("Phase change for $N={0}$".format(num_agents), fontdict=TITLEFONT)
    ax.set_ylabel('Frac. Feasible', fontdict=YFONT)
    ax2.set_ylabel('Avg. Runtime (s)', fontdict=YFONT)
    ax.set_xlabel("$M$", fontdict=XFONT)

    plt.legend([proxy_feas, proxy_solve],
               ["Frac. Feasible", "Solve Time (s)"],
               loc='upper right',
               )
    plt.savefig("phase_transition_n{0}.pdf".format(num_agents), format='pdf', bbox_inches='tight')
    plt.clf()
    
