Fig. 11: Cloud Gaming
=====

Our analysis builds on the paper "Dissecting Cloud Gaming Performance with DECAF" [0] who published their code at [decafCG/decaf](https://github.com/decafCG/decaf).
We applied small changes to their analysis script and published our changes at [hendrikcech/decaf](https://github.com/hendrikcech/decaf).

[0] Hassan Iqbal, Ayesha Khalid, and Muhammad Shahzad. 2021. Dissecting Cloud Gaming Performance with DECAF. Proc. ACM Meas. Anal. Comput. Syst. 5, 3, Article 31 (December 2021), 27 pages. https://doi.org/10.1145/3491043

# Setup
## Dataset
Please fetch the gaming dataset and point env var `DATA_PATH` to it. This dataset contains both the raw data captured during the experiment and the artifacts created by the DECAF analysis scripts.

The dataset contains multiple measurement runs, each 30 minutes long, over different links: Ethernet, Starlink, and cellular 5G. Each folder has the following structure.
``` sh
crew_fr_30_ethernet1
--- Captured at measurement time
├── bot_log.csv      # timestamped game bot actions performed during the measurement
├── dump_for_ip.pcapng
├── dump.pcapng      # full packet trace from measurement run
├── ips.json # detected client and server IPs
├── rtcStatsCollector.txt # written by Chrome during measurement
├── video_1684482973.512462.mkv
---- Created by data_processing.py in post-processing
├── current_rtt.json
├── frame_timestamps.json
├── packet_loss_stats.json
├── parsed_rtcStatsCollector.json
├── parsed_videoReceiveStream.json
├── predicted_files.json
├── video_cropped.mkv
├── videoReceiveStream.txt
└─── vrs_summary_stats.json
```

### 0. Optional: DECAF Artifact Processing
Clone our adapted decaf version:

``` sh
git submodule update --init --recursive
```

Please follow the setup instructions in `decaf/data_processing/README.md` and run `decaf/data_processing/data_processing.py`. Afterwards, compute our custom statistics with `bash preprocessing.sh` with `DATA_PATH` and `RESULT_PATH` being set.

### 1. Run our Analysis and Plotting Scripts
Set the environment variables `DATA_PATH` and `RESULT_PATH`. To recreate Fig. 11 from our paper, run `bash plot.sh`.
