#!/usr/bin/env bash

set -eux

# Remember that envvar DATA_PATH needs to point to the cloned dataset (see the previous step)
export DATA_PATH="TODO"
export RESULT_PATH="$(pwd)/results"

echo "Expecting dataset in\tDATA_PATH=$DATA_PATH"
echo "Writing results to\tRESULT_PATH=$RESULT_PATH"

# RIPE Atlas plots
jupyter nbconvert --to=html --output-dir="$RESULT_PATH" --execute ripe_atlas_figures/ripe_atlas_repr.ipynb

# MLab plots
jupyter nbconvert --to=html --output-dir="$RESULT_PATH" --execute mlab_figures/mlab_concise.ipynb

# Zoom plots
bash zoom/plot.sh

# Cloud gaming plots
bash gaming/plot.sh

# Controlled experiments (Figure 16)
bash controlled/16a/generate_fig_16a.sh   # Generate Figure 16a
bash controlled/16b/generate_fig_16b.sh   # Generate Figure 16b
bash controlled/16c/generate_fig_16c.sh   # Generate Figure 16c
