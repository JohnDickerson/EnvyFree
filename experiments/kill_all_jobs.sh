#!/bin/bash

read -p "REALLY kill all your jobs? <y/n>?  "
[ "$REPLY" != "y" ] && exit

./view_jobs.sh | cut -d'.' -f1 | xargs qdel

