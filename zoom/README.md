Fig. 10: Zoom Video Conferencing
====

# Setup
## Get the data
Download the data set.

## Optional: Recompute the Zoom Statistics
We used the Zoom analysis tools published by Michel et al. [0] at [Princeton-Cabernet/zoom-analysis](https://github.com/Princeton-Cabernet/zoom-analysis) to compute Zoom statistics from captured packet traces at the call parties. Our data set already includes the computed metrics but you can optionally recreate them.

To recompute the traces, load the zoom analysis source by running `git submodule update --init --recursive`.
Please follow their compiliation instructions in [zoom-analysis/README.md](zoom-analysis/README.md) to build the `zoom_flows` and `zoom_rtp` binaries.
Make sure to include them in your PATH: `export PATH="$(pwd)/zoom-analysis/build:$PATH"`.

Process the files using our utility script: `bash process_pcaps.sh`

[0] Oliver Michel, Satadal Sengupta, Hyojoon Kim, Ravi Netravali, and Jennifer Rexford. 2022. Enabling passive measurement of zoom performance in production networks. In Proceedings of the 22nd ACM Internet Measurement Conference (IMC '22). Association for Computing Machinery, New York, NY, USA, 244–260. https://doi.org/10.1145/3517745.3561414

## Recreate the Plots
Set the environment variables `DATA_PATH` and `RESULT_PATH`. Run `bash plot.sh` to create the figure.
