#!/bin/bash

if [ -z "$DATA_PATH" ] || [ -z "$RESULT_PATH" ]; then echo "DATA_PATH and RESULT_PATH need to be set"
    exit 1
fi
mkdir -p "$RESULT_PATH/controlled"

cd "$(dirname -- "$0")"

# Convert the relevent data from the dish from raw iperf logs to an SQLite DB
rm uplink.db downlink.db || true # cleanup
python ./parse_iperf.py "$DATA_PATH/controlled/iperf/dish-2"

# Create the plot
python ./plot.py
mv throughput.pdf "$RESULT_PATH/controlled/fig16b_throughput.pdf"
mv throughput.svg "$RESULT_PATH/controlled/fig16b_throughput.svg"
