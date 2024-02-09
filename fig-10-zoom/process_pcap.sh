#!/usr/bin/env sh

set -eu

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <pcap>"
    exit 1
fi

PCAP="$1"
DIR="$(dirname "$PCAP")"

zoom_flows --in "$PCAP" --zpkt-out "$DIR/zpkt.zpkt"
zoom_rtp --in "$DIR/zpkt.zpkt" -s "$DIR/streams.csv" -p "$DIR/packets.csv" -f "$DIR/frames.csv" -t "$DIR/stats.csv"
