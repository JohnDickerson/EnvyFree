#!/bin/csh

###### Number of CPUs MUST be a multiple of 16
#PBS -l ncpus=128
#PBS -l walltime=8:00:00

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
cp $HOME/code/EnvyFree/trunk/*.py .

# Make sure we're running the right Python ...
source /usr/share/modules/init/csh
module load python/2.7.3

# Start seed value -- we increment as we use it
set SEED = `date +%s`
# Number of repeat random runs per parameter vector setting
set NUM_REPEATS = 1
# Objective: either --obj-feas or --obj-social
#set OBJECTIVE = "--obj-feas"  # set via outer script
# Utility distribution: --dist-urand-int, --dist-urand-real, --dist-zipf-real
#                       --dist-polya-urn-real, or --dist-correlated-real
#set DISTRIBUTION = "--dist-urand-real"   # set via outer script
# Iterate over #agents:  range($N_MIN, $N_MAX, $N_STEP)
#set N_MIN = 3  # set via outer script
#set N_MAX = 10 # set via outer script 
set N_STEP = 1
# Iterate over #items:  range($M_MIN, $M_MAX, $M_STEP)
#                       (the Python code will skip #items<#agents)
set M_MIN = 3
set M_MAX = 100
set M_STEP = 1

# Start one big serial Python loop on each blade
set COUNTER = 0
set MAX = 16    # CHECK:  MAX <= 1/8 of number of CPUs requested
while ( $COUNTER < $MAX )

    # Want a different seed for each of the instances
    #set SEED=`dd if=/dev/urandom count=1 2> /dev/null | cksum | cut -f1 -d" "`
    @ SEED++

    # Runtime output will be stored here
    set OUTBASE=out${OBJECTIVE}_${DISTRIBUTION}_${N_MIN}_${SEED}

    # Run the Python script for E-F allocations (background process!)
    # Run multiple times with same seed: {fathom, no fathom} x {priority, no priority} x {max value branching, no max value branching}
    # NO FATHOMING
    set OUTFILE=${OUTBASE}a.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP  &
    set OUTFILE=${OUTBASE}b.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP --branch-avg-value &
    set OUTFILE=${OUTBASE}c.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP --prioritize-avg-value &
    set OUTFILE=${OUTBASE}d.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP --branch-avg-value --prioritize-avg-value &

    # NO FATHOMING
    set OUTFILE=${OUTBASE}e.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP --fathom-too-much-envy  &
    set OUTFILE=${OUTBASE}f.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP --branch-avg-value --fathom-too-much-envy &
    set OUTFILE=${OUTBASE}g.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP --prioritize-avg-value --fathom-too-much-envy &
    set OUTFILE=${OUTBASE}h.csv
    python driver.py --filename $OUTFILE --num_repeats $NUM_REPEATS $OBJECTIVE $DISTRIBUTION --seed $SEED -n $N_MIN $N_MAX $N_STEP -m $M_MIN $M_MAX $M_STEP --branch-avg-value --prioritize-avg-value --fathom-too-much-envy &

    @ COUNTER++
end

# Wait for all our little serial children to finish
wait

#cp $SCRATCH/*.csv $HOME/

ja -chlst $HOME/ja.$PBS_JOBID
