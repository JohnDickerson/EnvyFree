Plotting scripts for `driver.py`
================================

This directory contains scripts for the plots contained in our AAAI-2014 submission.

*  `graph_phase_change.py`
   
   Generic phase change and hardness bump plotting code, takes input that can vary {objective type, distribution type, number of agents, number of items}, but assumes any branching rules, prioritizations, or CPLEX tweaks are identical across runs.

*  `graph_comparison.py`:

   Plotting code that compares timing and node counts for different combinations of branching rules, variable prioritizations, and CPLEX tweaks across multiple runs, matching on seed (first column in `driver.py` output).  

* `graph_utility_distributions.py`: 

  Quick plot used to visualization different distributions from which we draw valuations.

* `data_utils.py`:
  
  Mainly I/O helpers for loading .csv files from `driver.py`