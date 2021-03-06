#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.patches as patches   # For the proxy twin-axis legend entry
from data_utils import IOUtil

# Raw .csv file containing data
#filename_data = "../data/comparison_models_12hr.csv"
filename_data = "../data/big_st_social_welfare.csv"

# Some of the older runs have a different .csv structure
using_old_data = True
if using_old_data:
    from data_utils import OldCol as Col
else:
    from data_utils import Col as Col

# Include two extra lines, for solve time (feasible) and solve time (infeasible)?
plot_all_lines = True

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

XFONT={'fontsize':24}
YFONT={'fontsize':24}
TITLEFONT={'fontsize':24}
TINYFONT={'fontsize':6}
TICKFONT={'fontsize':16}

# Should we use a timeout penalty?  If so, how much?
timeout_penalty_on = True
timeout_penalty_s = 1 * (12*60*60)   # K*12hr penalty
print "Timeout penalty: {0} @ {1} seconds".format(timeout_penalty_on, timeout_penalty_s)

# Plot averages or medians for runtime?
do_average = False
print "Plotting", ("average" if do_average else "median"), "runtimes."

# Load all the data at once (OLDER data)
data = IOUtil.load_old_data(filename_data)

# Grab proper iteration data
num_agents_list = np.unique(data[:,Col.num_agents])
num_items_list = np.unique(data[:,Col.num_items])
dist_type_list = np.unique(data[:,Col.dist_type])
obj_type_list = np.unique(data[:,Col.obj_type]) 

dashes = [
    '-', #   : solid line
    ':',  #   : dotted line
    '-.',  #   : dashed line
    '--', #   : dash-dot line
    ]

# Make the phase transition graphs
for obj_type in obj_type_list:

    for dist_type in dist_type_list:

        for num_agents in num_agents_list:

            #if num_agents != 10: continue
            num_items_list = range(int(num_agents),30)

            print "Obj={0}, Dist={1}, N={2} ...".format(IOUtil.obj_type_map[int(obj_type)], IOUtil.dist_type_map[int(dist_type)], int(num_agents)) 

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
            old_data_ct = -1
            for num_items in num_items_list:

                # Grab just the data for this {number of agents, number of items}
                data_num_items = [row for row in data_num_agents 
                                  if row[Col.num_items] == num_items]

                data_feas = np.array([row[Col.feasible] for row in data_num_items])
                data_solve_s = np.array([row[Col.solve_s] for row in data_num_items])

                # If we're on the first data point, assume no timeouts and start recording old data points
                if old_data_ct <= 0:
                    timeout_ct = 0
                else:
                    timeout_ct = old_data_ct - len(data_solve_s)
                old_data_ct = len(data_solve_s)

                if len(data_solve_s) > 0:
                    any_data = True

                    if timeout_penalty_on:
                        data_solve_s = np.append( data_solve_s, [timeout_penalty_s]*timeout_ct )

                feas_frac = np.average(data_feas)
                if feas_frac >= 0.99:
                    print "W.h.p. exists @ n={0}, m={1}".format(int(num_agents), int(num_items))

                y_feas.append( feas_frac )
                
                if do_average:
                    y_solve_s.append( np.average(data_solve_s) )
                else:
                    y_solve_s.append( np.median(data_solve_s) )

                data_solve_s_feas = np.array([row[Col.solve_s] for row in data_num_items
                                              if int(row[Col.feasible]) == 1])
                data_solve_s_infeas = np.array([row[Col.solve_s] for row in data_num_items
                                                if int(row[Col.feasible]) == 0])        
                if len(data_solve_s_feas) == 0:
                    y_solve_s_feas.append( None )
                else:
                    if do_average:
                        y_solve_s_feas.append( np.average(data_solve_s_feas) )
                    else:
                        y_solve_s_feas.append( np.median(data_solve_s_feas) )

                if len(data_solve_s_infeas) == 0:
                    y_solve_s_infeas.append( None )
                else:
                    if do_average:
                        y_solve_s_infeas.append( np.average(data_solve_s_infeas) )
                    else:
                        y_solve_s_infeas.append( np.median(data_solve_s_infeas) )

            # If we didn't read any valid data points (solve times), skip plotting
            if not any_data:
                continue

            # Plot both lines (%feas and runtime) on same x-axis, with two y-axes
            fig = plt.figure()
            ax = fig.add_subplot(111)
            plot_ct = 0  # Restart our indexing into linestyles
            plot_feas = ax.plot(num_items_list, y_feas, label="Frac. Feasible",
                                color='crimson',
                                linestyle=dashes[plot_ct % len(dashes)],
                                linewidth=2,
                                )
            plot_ct += 1
            
            # Fraction feasible is in [0,1]
            plt.ylim(0.0, 1.0)
            try:
                #ax.set_xscale('log')
                pass
            except ValueError:
                print "Skipping log-scale for N={0:d}".format(int(num_agents))
                ax.set_xscale('linear')

            ax2 = ax.twinx()
            plot_solve = ax2.plot(num_items_list, y_solve_s, label="Solve Time (s)",
                                  color='black',
                                  linestyle=dashes[plot_ct % len(dashes)],
                                  linewidth=2,
                                  )
            plot_ct += 1

            if plot_all_lines:
                plot_solve_feas = ax2.plot(num_items_list, y_solve_s_feas, label="Solve Time (feas)",
                                           color='black',
                                           linestyle=dashes[plot_ct % len(dashes)],
                                           )
                plot_ct += 1

                plot_solve_infeas = ax2.plot(num_items_list, y_solve_s_infeas, label="Solve Time (infeas)",
                                             color='black',
                                             linestyle=dashes[plot_ct % len(dashes)],
                                             )
                plot_ct += 1

            # Prettify the plot
            ax.set_title("$n={0:d}$, {1}, {2}".format(int(num_agents), IOUtil.obj_type_map[int(obj_type)], IOUtil.dist_type_map[int(dist_type)]), fontdict=TITLEFONT)
            ax.set_ylabel('Fraction Feasible', fontdict=YFONT)
            if do_average:
                ax2.set_ylabel('Average Runtime (s)', fontdict=YFONT)
            else:
                ax2.set_ylabel('Median Runtime (s)', fontdict=YFONT)

            ax.set_xlabel("$m$", fontdict=XFONT)
            ax.tick_params(axis='both', which='major', labelsize=TICKFONT['fontsize'])
            ax2.tick_params(axis='both', which='major', labelsize=TICKFONT['fontsize'])

            lns = plot_feas + plot_solve 
            if plot_all_lines: lns += plot_solve_feas + plot_solve_infeas    
            labs = [l.get_label() for l in lns]
            plt.legend(lns, labs, loc='upper right',)

            plt.savefig("phase_transition_n{0:d}_objtype{1:d}_dist{2:d}.pdf".format(int(num_agents), int(obj_type), int(dist_type)), format='pdf', bbox_inches='tight')
            plt.clf()

