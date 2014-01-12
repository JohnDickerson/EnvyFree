#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches   # For the proxy twin-axis legend entry

# Raw .csv file containing data
filename_data = "../data/big_st_social_welfare.csv"

# Include two extra lines, for solve time (feasible) and solve time (infeasible)?
plot_all_lines = False

# Maps column indices to the data they hold
class Col:
    (seed, 
     num_threads, 
     num_agents, 
     num_items, 
     dist_type, 
     N, 
     obj_type, 
     fathom_too_much_envy_on, fathom_too_much_envy_ct,
     branch_avg_value_on, branch_avg_value_ct,
     branch_sos1_envy_on, branch_sos1_envy_ct,
     prioritize_avg_value_on,
     feasible, 
     mip_node_count,
     build_s, 
     solve_s) = range(18)

obj_type_map = {0: "Existence", 1: "Social Welfare Max"}
dist_type_map = {1: "U[0,1]", 4: "Correlated"}

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
                    converters={Col.feasible: get_boolean_from_string,
                                Col.fathom_too_much_envy_on: get_boolean_from_string,
                                Col.branch_avg_value_on: get_boolean_from_string,
                                Col.branch_sos1_envy_on: get_boolean_from_string,
                                Col.prioritize_avg_value_on: get_boolean_from_string,
                                }, 
                    )
print 'Loaded ' + str(len(data)) + ' rows of data.'

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
            y_feas = []
            y_solve_s = []
            y_solve_s_feas = []
            y_solve_s_infeas = []

            any_data = False
            for num_items in num_items_list:

                # Grab just the data for this {number of agents, number of items}
                data_num_items = [row for row in data_num_agents 
                                  if row[Col.num_items] == num_items]

                data_feas = np.array([row[Col.feasible] for row in data_num_items])
                data_solve_s = np.array([row[Col.solve_s] for row in data_num_items])

                if len(data_solve_s) > 0:
                    any_data = True

                y_feas.append( np.average(data_feas) )
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
            plot_feas = ax.plot(num_items_list, y_feas,
                                color='crimson',
                                )
            proxy_feas = matplotlib.patches.Rectangle((0,0), width=1, height=0.1, facecolor='crimson')

            # Fraction feasible is in [0,1]
            plt.ylim(0.0, 1.0)
            try:
                ax.set_xscale('log')
            except ValueError:
                print "Skipping log-scale for N={0:d}".format(int(num_agents))
                ax.set_xscale('linear')

            ax2 = ax.twinx()
            plot_solve = ax2.plot(num_items_list, y_solve_s,
                                  color='black',
                                  )
            proxy_solve = matplotlib.patches.Rectangle((0,0), width=1, height=0.1, facecolor='black')

            if plot_all_lines:
                plot_solve_feas = ax2.plot(num_items_list, y_solve_s_feas,
                                           color='DarkBlue',
                                           #linestyle='-^',
                                           )
                proxy_solve_feas = matplotlib.patches.Rectangle((0,0), width=1, height=0.1, facecolor='DarkBlue')

                plot_solve_infeas = ax2.plot(num_items_list, y_solve_s_infeas,
                                             color='DarkGreen',
                                             #linestyle='-o',
                                             )
                proxy_solve_infeas = matplotlib.patches.Rectangle((0,0), width=1, height=0.1, facecolor='DarkGreen')

            # Prettify the plot
            ax.set_title("$N={0:d}$, {1}, {2}".format(int(num_agents), obj_type_map[int(obj_type)], dist_type_map[int(dist_type)]), fontdict=TITLEFONT)
            ax.set_ylabel('Fraction Feasible', fontdict=YFONT)
            ax2.set_ylabel('Average Runtime (s)', fontdict=YFONT)
            ax.set_xlabel("$M$", fontdict=XFONT)

            if plot_all_lines:
                plt.legend([proxy_feas, proxy_solve, proxy_solve_feas, proxy_solve_infeas],
                           ["Frac. Feasible", "Solve Time (s)", "Solve Time (feas)", "Solve Time (infeas)"],
                           loc='upper right',
                           )
            else:
                plt.legend([proxy_feas, proxy_solve],
                           ["Frac. Feasible", "Solve Time (s)"],
                           loc='upper right',
                           )

            plt.savefig("phase_transition_n{0:d}_objtype{1:d}_dist{2:d}.pdf".format(int(num_agents), int(obj_type), int(dist_type)), format='pdf', bbox_inches='tight')
            plt.clf()

