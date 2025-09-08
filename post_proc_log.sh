#!/bin/bash

# This dirty and ugly script post-processes the dirty logging of `calculate_mixing_length`
# Subroutine inputs and outputs. 

HELP="""
Usage: $0 <logfile> <output>

This dirty and ugly script post-processes the dirty logging of 'calculate_mixing_length'
subroutine inputs and outpusts.

Takes the STDERR output from a file and splits it into CSV files for each variable.
The files will be placed in the <output> directory.
It will be created if it does not exist.
"""

if [ "$#" -ne 2 ]; then
    echo "${HELP}"
    exit 1
fi

LOGPREFIX="LOGPREFIX"
GRIDPREFIX="GRIDPREFIX"
FILE=$1
OUTPUT=$2



if [ ! -d ${OUTPUT} ]; then
    mkdir -p ${OUTPUT}
fi

# Extract argumnets
for var in "thvm" "thlm" "rtm" "em" "exner" "p_in_Pa" "thv_ds" "Lscale" "Lscale_up" "Lscale_down"; do
    PATTERN="^${LOGPREFIX}: ${var} ="
    grep "${PATTERN}" ${FILE} | sed -e "s/${PATTERN}//" > ${OUTPUT}/${var}.csv 
done

# Extract grid info
PATTERN="^${GRIDPREFIX}:"
grep "${PATTERN}" ${FILE} | sed -e "s/${PATTERN}//" > ${OUTPUT}/grid_file


