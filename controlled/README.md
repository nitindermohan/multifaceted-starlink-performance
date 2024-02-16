
Fig. 16: Controlled Measurements
=====
The scripts in the subdirectories generate the four parts of Figure 16:
1. Figure 16a: analysis of Starlink round-trip latencies.
2. Figure 16b: analysis of Starlink uplink and downlink throughput.
3. Figure 16c (upper): analysis of Starlink round-trip latencies when connected to a single serving satellite.
4. Figure 16c (lower): analysis of the time between the connectivity window start / end and the previous reconfiguration interval (for more details see the paper).

# Setup

## Dataset

Please fetch the dataset and point env var `DATA_PATH` to it. Note that only a small subset of the entire dataset is required to produce the figures, specifically the following eight files.
``` sh
data
└── controlled
    ├── irtt
    │   ├── dish-1
    │   │   └── 230417T120001_irtt.json.zst
    │   └── dish-2
    │       └── irtt.zst
    ├── iperf
    │   └── dish-2
    │       ├── downlink_20230515T130700.txt
    │       └── uplink_20230515T130000.txt
    ├── irtt_fov
    │   └── 2023-10-08_18-41-11.json
    └── grpc_fov
        ├── 2023-05-16_to_2023-05-19.db
        ├── 2023-10-08_to_2023-10-11.db
        └── 2023-10-12_to_2023-10-13.db
```

## Running the plotting scripts

To re-create Figure 16 from the paper, simply run the appropriate scripts.
``` sh
cd 16a && ./generate_fig_16a.sh      # Generate Figure 16a
cd ../16b && ./generate_fig_16b.sh   # Generate Figure 16b
cd ../16c && ./generate_fig_16c.sh   # Generate Figure 16c
```
