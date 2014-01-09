#!/bin/csh

###### Number of CPUs MUST be a multiple of 16
#PBS -l ncpus=16
#PBS -l walltime=01:00:00

###### combine stderr and stdout to one file
#PBS -j oe

######
#PBS -q batch

###### Need to export CPLEX Python API path
#PBS -v PYTHON_PATH

set echo
ja $HOME/ja.$PBS_JOBID

###### Scratch is a testbed, all files auto-deleted after >7 days!
cd $SCRATCH

# Copy necessary files (all .py files) to $SCRATCH
cp $HOME/code/EnvyFree/*.py .

# Make sure we're running the right Python ...                                  
module load python/2.7.3

# Start seed value -- we increment as we use it
set SEED = `date +%s`
# Number of repeat random runs per parameter vector setting
set NUM_REPEATS = 25
# Objective: either --obj-feas or --obj-social
set OBJECTIVE = "--obj-feas"      
# Utility distribution: --dist-urand-int, --dist-urand-real, --dist-zipf-real
#                       --dist-polya-urn-real, or --dist-correlated-real
set DISTRIBUTION = "--dist-urand-real"
# Iterate over #agents:  range($N_MIN, $N_MAX, $N_STEP)
set N_MIN = 3
set N_MAX = 10
set N_STEP = 1
# Iterate over #items:  range($M_MIN, $M_MAX, $M_STEP)
#                       (the Python code will skip #items<#agents)
set M_MIN = 3
set M_MAX = 100
set M_STEP = 1

# Start one big serial Python loop on each blade
set COUNTER = 0
set MAX = 16    # CHECK:  MAX <= number of CPUs requested
while ( $COUNTER < $MAX )

    # Want a different seed for each of the instances
    #set SEED=`dd if=/dev/urandom count=1 2> /dev/null | cksum | cut -f1 -d" "`
    @ SEED++

    # Runtime output will be stored here
    set OUTFILE=out_ef_$SEED.csv

    # Run the Python script for E-F allocations (background process!)
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP  &

    @ COUNTER++
end

# Wait for all our little serial children to finish
wait

#cp $SCRATCH/*.csv $HOME/

ja -chlst $HOME/ja.$PBS_JOBID
