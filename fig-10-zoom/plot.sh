#!/usr/bin/env sh

set -xeu

cd "$(dirname -- "$0")"

DATA="$DATA_PATH/zoom"
RES="result"

mkdir -p "$RES"

echo "Plotting Fig 10 Zoom"
python plot_xtime_figure.py \
    "$DATA"/20231011_ter_gpu/01 "$DATA"/20231011_stl_gpu/01 \
    --view-ter 90,145 --view-stl 120,175 \
    --save "$RES/fig-10-zoom.pdf"

echo "Generating Zoom statistics"
python boxplots.py \
    --stl  "$DATA"/20231011_stl_gpu/{01,02,03,04,05,06} \
    --ter  "$DATA"/20231011_ter_gpu/{01,02,03,04,05,06} \
    --save "$RES/zoom-boxplot.pdf" \
    --csv  "$RES/zoom_metrics.csv"
