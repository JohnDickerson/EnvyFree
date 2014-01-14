#!/bin/bash

tmpbase=__tmp__
seedbase=1389664136
reps=10

# Run ${reps} times using the same model, different parameters
for ((i=0; i<${reps}; i++ ))
do
    seed=`expr ${seedbase} + ${i}`
    out=${tmpbase}${seed}
    VERSIONER_PYTHON_PREFER_32_BIT=yes python driver.py -f ${out}A -n 8 9 1 -m 14 15 1 --seed ${seed} --num_repeats 1 --obj-feas --dist-urand-real 
    VERSIONER_PYTHON_PREFER_32_BIT=yes python driver.py -f ${out}B -n 8 9 1 -m 14 15 1 --seed ${seed} --num_repeats 1 --obj-feas --dist-urand-real --fathom-too-much-envy
done

# Combines all runs from each parameter vector into a single file;
# keeps the big file, deletes all the temporary single run files
# Also print some statistics for easy comparison
for suffix in A B
do
    newsuffix=`echo ${suffix} | tr "A-M" "N-Z"`
    cat ${tmpbase}*${suffix} > ${tmpbase}${newsuffix}.csv
    rm -f ${tmpbase}*${suffix}
    cat ${tmpbase}${newsuffix}.csv | grep '8,14,' | cut -d',' -f 1,5,7,8,15 > ${tmpbase}${newsuffix}_feas.csv
done

