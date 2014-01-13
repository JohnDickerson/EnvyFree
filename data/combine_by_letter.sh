#!/bin/bash

for suffix in a b c d e f g h
do
    cat *${suffix}.csv > comp_${suffix}.csv
done
