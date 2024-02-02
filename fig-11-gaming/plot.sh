#!/usr/bin/env bash

set -xeu

cd "$(dirname -- "$0")"

DATA="$(dirname -- "$0")/data"
RES="$(dirname -- "$0")/result"

for c in ethernet starlink cellular; do
    python compute_overall_metrics.py "$DATA"/crew*${c}* --method overall    --save "$RES/metrics_${c}.json"
    python compute_overall_metrics.py "$DATA"/crew*${c}* --method per_minute --save "$RES/metrics_resampled_${c}.json"
done

for c in ethernet starlink cellular; do
    python compute_delay.py "$DATA"/crew*${c}* --save   "$RES/delays_${c}.csv"
    python compute_delay.py "$DATA"/crew*${c}* --savets "$RES/delays_ts_${c}.csv"
done

python inspect_xtime.py --dirs "$DATA/crew_mo_30_cellular2" "$DATA/crew_fr_30_starlink3" --gdelays "$DATA"/delays_ts_{cellular,starlink}.csv --views 700,730 700,730 --save "$RES/fig-11-gaming.pdf"
