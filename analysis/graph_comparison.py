#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches   # For the proxy twin-axis legend entry

from data_utils import Col, IOUtil

# Raw .csv file containing data
filename_data = "../data/comparison_models.csv"

# Verbose (prints stats on #data points
verbose = False

# Should we use a timeout penalty?  If so, how much?
timeout_penalty_on = True
timeout_penalty_s = 10 * (8*60*60)
print "Timeout penalty: {0} @ {1} seconds".format(timeout_penalty_on, timeout_penalty_s)

# Which combinations of parameters should we plot?
plot_list = [
    {'on': True, 'x': [0,0,0,0], 'disp': 'Model 1'},
    {'on': False, 'x': [0,0,1,0], 'disp': 'Prioritize'},
    {'on': False, 'x': [0,1,0,0], 'disp': 'Branch Avg.'},
    {'on': False, 'x': [0,1,1,0], 'disp': 'Branch and Prioritize Avg.'},
    {'on': False, 'x': [1,0,0,0], 'disp': 'Fathom'},
    {'on': False, 'x': [1,0,1,0], 'disp': 'Fathom, Prioritize'},
    {'on': False, 'x': [1,1,0,0], 'disp': 'Fathom, Branch Avg.'},
    {'on': False, 'x': [1,1,1,0], 'disp': 'Fathom, Branch and Prioritize Avg.'},
    {'on': True, 'x': [0,0,0,1], 'disp': 'Model 2'},
    ]
tweak_map = [
    Col.fathom_too_much_envy_on, 
    Col.branch_avg_value_on, 
    Col.prioritize_avg_value_on,
    Col.alternate_IP_model_on,
    ]


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
#num_items_list = np.unique(data[:,Col.num_items])
dist_type_list = np.unique(data[:,Col.dist_type])
obj_type_list = np.unique(data[:,Col.obj_type]) 

dashes = [
    '-.', #   : dashed line
    '-',  #   : solid line
    '--', #   : dash-dot line
    ':',  #   : dotted line
    ]

# Make the phase transition graphs
for obj_type in obj_type_list:

    for dist_type in dist_type_list:

        for num_agents in num_agents_list:

            if num_agents != 10 and num_agents != 6: continue
            num_items_list = range(int(num_agents),30)

            print "Obj={0}, Dist={1}, N={2} ...".format(IOUtil.obj_type_map[int(obj_type)], IOUtil.dist_type_map[int(dist_type)], int(num_agents)) 

            data_num_agents = [row for row in data 
                               if row[Col.num_agents] == num_agents 
                               and row[Col.dist_type] == dist_type
                               and row[Col.obj_type] == obj_type
                               ]
            
            # Plot all parameterizations on the same canvas
            fig = plt.figure()
            ax = fig.add_subplot(111)
            plot_ct = 0  # Restart our indexing into linestyles

            for params in plot_list:
                
                # Make sure we want to plot this line
                if not params['on']:
                    continue

                # Only get correct branch+prioritization data
                specific = [row for row in data_num_agents
                            if row[tweak_map[0]] == params['x'][0]
                            and row[tweak_map[1]] == params['x'][1]
                            and row[tweak_map[2]] == params['x'][2]
                            and row[tweak_map[3]] == params['x'][3]
                            ]

                # Want to plot (a) %feasible and (b) runtime to prove opt/infeas
                y_solve_s = []
                y_feas = []
                y_solve_s_feas = []
                y_solve_s_infeas = []

                any_data = False
                data_pt_count = 0
                old_data_ct = -1
                for num_items in num_items_list:
                    
                    # Grab just the data for this {number of agents, number of items}
                    data_num_items = [row for row in specific 
                                      if row[Col.num_items] == num_items]
                    data_solve_s = np.array([row[Col.solve_s] for row in data_num_items])
                    data_feas = np.array([row[Col.feasible] for row in data_num_items])
                    data_solve_s_feas = np.array([row[Col.solve_s] for row in data_num_items
                                                  if int(row[Col.feasible]) == 1])
                    data_solve_s_infeas = np.array([row[Col.solve_s] for row in data_num_items
                                                    if int(row[Col.feasible]) == 0])

                    # If we're on the first data point, assume no timeouts and start recording old data points
                    if old_data_ct <= 0:
                        timeout_ct = 0
                    else:
                        timeout_ct = old_data_ct - len(data_solve_s)
                    old_data_ct = len(data_solve_s)

                    if verbose and num_agents > 6:
                        print "N={0} M={1} Data={2} Dropped={3}".format(int(num_agents), int(num_items), len(data_solve_s), timeout_ct)
                        
                    if len(data_solve_s) > 0:
                        any_data = True

                        if timeout_penalty_on:
                            data_solve_s = np.append( data_solve_s, [timeout_penalty_s]*timeout_ct )

                        y_solve_s.append( np.average(data_solve_s) )
                        y_feas.append( np.average(data_feas) )

                    else:
                        y_solve_s.append( None )
                        y_feas.append( None )

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

                ax.plot(num_items_list, y_solve_s,
                        color='black',
                        linestyle=dashes[plot_ct % len(dashes)],
                        label=params['disp']
                        )
                plot_ct += 1

                try:
                    #ax.set_xscale('log')
                    pass
                except ValueError:
                    print "Skipping log-scale for N={0:d}".format(int(num_agents))
                    ax.set_xscale('linear')

            # Prettify the plot
            ax.set_title("$N={0:d}$, {1}, {2}".format(int(num_agents), IOUtil.obj_type_map[int(obj_type)], IOUtil.dist_type_map[int(dist_type)]), fontdict=TITLEFONT)
            ax.set_ylabel('Average Runtime (s)', fontdict=YFONT)
            ax.set_xlabel("$M$", fontdict=XFONT)

            plt.legend(
                       #prop={'size':6},
                       loc='upper right',
                       )

            plt.savefig("comparison_n{0:d}_objtype{1:d}_dist{2:d}.pdf".format(int(num_agents), int(obj_type), int(dist_type)), format='pdf', bbox_inches='tight')
            plt.clf()

