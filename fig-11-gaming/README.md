Fig. 11: Cloud Gaming
=====

Our analysis builds on the paper "Dissecting Cloud Gaming Performance with DECAF" [0] who published their code at [decafCG/decaf](https://github.com/decafCG/decaf).
We applied small changes to their analysis script and published our changes at [hendrikcech/decaf](https://github.com/hendrikcech/decaf).

[0] Hassan Iqbal, Ayesha Khalid, and Muhammad Shahzad. 2021. Dissecting Cloud Gaming Performance with DECAF. Proc. ACM Meas. Anal. Comput. Syst. 5, 3, Article 31 (December 2021), 27 pages. https://doi.org/10.1145/3491043

# Setup
## Get the data
rsync gaming data from dataset to /data.
This dataset already contains the artifacts that the decaf analysis scripts produce.
To regenerate these, follow the instructions included in the decaf repository.

The data was recorded
``` sh
crew_fr_30_ethernet1
├── bot_log.csv
├── cropped/
├── current_rtt.json
├── dump_for_ip.pcapng
├── dump.pcapng
├── extractedFrames
├── frames
├── frame_timestamps.json
├── ips.json
├── packet_loss_stats.json
├── parsed_rtcStatsCollector.json
├── parsed_videoReceiveStream.json
├── predicted_files.json
├── rtcStatsCollector.txt
├── uncropped
├── video_1684482973.512462.mkv
├── video_cropped.mkv
├── videoReceiveStream.txt
└── vrs_summary_stats.json
```

## decaf Artifact Processing: TODO
Clone our adapted decaf version:

``` sh
git submodule update --init --recursive
```

## Plotting
To recreate the plots and data that we reference in our paper, run `bash plot.sh`.
