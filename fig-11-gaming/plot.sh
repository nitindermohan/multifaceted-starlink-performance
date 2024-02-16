#!/usr/bin/env bash

set -xeu

cd "$(dirname -- "$0")"

DATA="$DATA_PATH/gaming"
RES="result"

mkdir -p "$RES"

python inspect_xtime.py \
    --dirs "$DATA/crew_mo_30_cellular2" "$DATA/crew_fr_30_starlink3" \
    --gdelays "$DATA"/gaming_delays_ts_{cellular,starlink}.csv \
    --views 700,730 700,730 \
    --save "$RES/fig-11-gaming.pdf"
