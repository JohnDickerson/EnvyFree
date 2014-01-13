#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches   # For the proxy twin-axis legend entry

from data_utils import Col, IOUtil

# Raw .csv file containing data
filename_data = "../data/comparison.csv"

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

XFONT={'fontsize':24}
YFONT={'fontsize':24}
TITLEFONT={'fontsize':24}
TINYFONT={'fontsize':6}

# Load data
data = IOUtil.load(filename_data)

# Grab proper iteration data
num_agents_list = np.unique(data[:,Col.num_agents])
num_items_list = np.unique(data[:,Col.num_items])
dist_type_list = np.unique(data[:,Col.dist_type])
obj_type_list = np.unique(data[:,Col.obj_type]) 

# Make the phase transition graphs
for obj_type in obj_type_list:

    for dist_type in dist_type_list:

        for num_agents in num_agents_list:

            data_num_agents = [row for row in data 
                               if row[Col.num_agents] == num_agents 
                               and row[Col.dist_type] == dist_type
                               and row[Col.obj_type] == obj_type
                               ]

            # Want to plot (a) %feasible and (b) runtime to prove opt/infeas
            y_solve_s = []
            y_solve_s_feas = []
            y_solve_s_infeas = []

            any_data = False
            for num_items in num_items_list:

                # Grab just the data for this {number of agents, number of items}
                data_num_items = [row for row in data_num_agents 
                                  if row[Col.num_items] == num_items]

                data_solve_s = np.array([row[Col.solve_s] for row in data_num_items])

                if len(data_solve_s) > 0:
                    any_data = True

                y_solve_s.append( np.average(data_solve_s) )

                data_solve_s_feas = np.array([row[Col.solve_s] for row in data_num_items
                                              if int(row[Col.feasible]) == 1])
                data_solve_s_infeas = np.array([row[Col.solve_s] for row in data_num_items
                                                if int(row[Col.feasible]) == 0])        
                if len(data_solve_s_feas) == 0:
                    y_solve_s_feas.append( None )
                else:
                    y_solve_s_feas.append( np.average(data_solve_s_feas) )

                if len(data_solve_s_infeas) == 0:
                    y_solve_s_infeas.append( None )
                else:
                    y_solve_s_infeas.append( np.average(data_solve_s_infeas) )

            # If we didn't read any valid data points (solve times), skip plotting
            if not any_data:
                continue

            # Plot both lines (%feas and runtime) on same x-axis, with two y-axes
            fig = plt.figure()
            ax = fig.add_subplot(111)

            plot_solve = ax.plot(num_items_list, y_solve_s,
                                  color='black',
                                  )

            # Fraction feasible is in [0,1]
            plt.ylim(0.0, 1.0)
            try:
                ax.set_xscale('log')
            except ValueError:
                print "Skipping log-scale for N={0:d}".format(int(num_agents))
                ax.set_xscale('linear')

            # Prettify the plot
            ax.set_title("$N={0:d}$, {1}, {2}".format(int(num_agents), IOUtil.obj_type_map[int(obj_type)], IOUtil.dist_type_map[int(dist_type)]), fontdict=TITLEFONT)
            ax.set_ylabel('Average Runtime (s)', fontdict=YFONT)
            ax.set_xlabel("$M$", fontdict=XFONT)

            plt.legend(
                       loc='upper right',
                       )

            plt.savefig("comparison_n{0:d}_objtype{1:d}_dist{2:d}.pdf".format(int(num_agents), int(obj_type), int(dist_type)), format='pdf', bbox_inches='tight')
            plt.clf()

