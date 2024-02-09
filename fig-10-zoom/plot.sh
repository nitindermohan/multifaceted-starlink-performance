#!/usr/bin/env sh

set -x

cd "$(dirname -- "$0")"

DATA="../fig-10-zoom-dataset"
RES="../result"

echo "Plot xtime"
python plot_xtime_figure.py \
    "$DATA"/20231011_ter_gpu/01 "$DATA"/20231011_stl_gpu/01 \
    --view-ter 90,145 --view-stl 120,175 \
    --save "$RES/fig-10-zoom.pdf"
