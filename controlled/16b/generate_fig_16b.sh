#!/bin/bash

cd "$(dirname -- "$0")"

# Convert the relevent data from the dish from raw iperf logs to an SQLite DB
python ./parse_iperf.py $DATA_PATH/controlled/iperf/dish-2

# Create the plot
python ./plot.py
