#!/usr/bin/env sh

set -xeu

cd "$(dirname -- "$0")"

DATA="$DATA_PATH/gaming"
RES="result"

mkdir -p "$RES"

for c in ethernet starlink cellular; do
    python compute_overall_metrics.py "$DATA"/crew*${c}* --method overall    --save "$RES/gaming_metrics_${c}.json"
    python compute_overall_metrics.py "$DATA"/crew*${c}* --method per_minute --save "$RES/gaming_metrics_resampled_${c}.json"
done

for c in ethernet starlink cellular; do
    python compute_delay.py "$DATA"/crew*${c}* --save   "$RES/gaming_delays_${c}.csv"
    python compute_delay.py "$DATA"/crew*${c}* --savets "$RES/gaming_delays_ts_${c}.csv"
done
