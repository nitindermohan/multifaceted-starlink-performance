#!/bin/bash

if [ -z "$DATA_PATH" ] || [ -z "$RESULT_PATH" ]; then echo "DATA_PATH and RESULT_PATH need to be set"
    exit 1
fi
mkdir -p "$RESULT_PATH/controlled"

cd "$(dirname -- "$0")"

# Create the plot
python ./plot.py "$DATA_PATH"
mv fov.pdf "$RESULT_PATH/controlled/fig16c_fov.pdf"
mv fov.svg "$RESULT_PATH/controlled/fig16c_fov.svg"
