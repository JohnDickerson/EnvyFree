#!/bin/bash
# Data should have N columns; sometimes, Blacklight cuts off a job
# during file write so we end up with < N columns.  This script cuts all
# lines that don't have (N-1) commas (i.e., N columns)

path=out.csv
temp=_temp_${path}_TEMP1234567.tmp
N=8

read -p "Remove all lines without ${N} columns from ${path}? <y/n>?  "
[ "$REPLY" != "y" ] && exit

touch ${temp}
while IFS= read -r line
do 
    col_count="${line//[^,]/}"
    col_count=`expr ${#col_count} + 1`
    if [ ! ${col_count} -eq ${N} ]
    then
	echo "Removing: ${line}"
    else
	echo ${line} >> ${temp}
    fi
done < ${path}
mv ${temp} ${path}
