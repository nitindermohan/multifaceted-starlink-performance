#!/usr/bin/env bash

cd "$(dirname -- "$0")"

DATA="../fig-10-zoom-dataset"

haz() {
      if hash $1 > /dev/null 2>&1; then
            return 0
      else
            return 1
      fi
}

if haz parallel; then
    echo "Processing the files in parallel"
    parallel --eta bash process_pcap.sh "{}" ::: "$DATA"/*/{0,1}*/{local,remote}/*pcap
else
    echo "parallel is not available, processing the files sequentially"
    for PCAP in "$DATA"/*/{0,1}*/{local,remote}/*pcap; do
        bash process_pcap.sh "$PCAP"
    done
fi
