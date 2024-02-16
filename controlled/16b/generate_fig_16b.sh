#!/bin/bash

# Convert the relevent data from the dish from raw iperf logs to an SQLite DB
./parse_iperf.py $DATA_PATH/controlled/iperf/dish-2

# Create the plot
./plot.py