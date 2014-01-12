#!/bin/csh
# Do not use except for legacy experiments; use run_qsubs.sh instead.

foreach n_min ( 2 3 4 5 6 7 8 9 10 )
    @ n_max = $n_min + 1
    qsub -vN_MIN=${n_min},N_MAX=${n_max} qsub-urandom.sh
    sleep 1
    qsub -vN_MIN=${n_min},N_MAX=${n_max} qsub-correlated.sh
    sleep 1
end
