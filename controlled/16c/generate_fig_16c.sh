#!/bin/bash

cd "$(dirname -- "$0")"

# Create the plot
python ./plot.py $DATA_PATH
