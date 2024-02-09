#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os.path
import argparse
from matplotlib.cbook import boxplot_stats
from matplotlib import rcParams
from matplotlib.backends.backend_pdf import PdfPages
import json
import multiprocessing
import sys

import zoom_parser as zp

def plot_external_legend(parts, figsize, **kwargs): # ncol =
    fig_legend = plt.figure(figsize=figsize)
    fig_legend.legend(parts, [p.get_label() for p in parts], **kwargs)
    fig_legend.tight_layout()
    return fig_legend

def compute_bxp_metrics(paths):
    streams = []
    packets = []
    packets_local = []
    packets_remote = []
    frames_local = []
    frames_remote = []

    for base_path in paths:
        local = os.path.join(base_path, "local")
        remote = os.path.join(base_path, "remote")

        streams.append(zp.read_streams_csv(local))

        df_packets_local = zp.read_packets_csv(local)
        df_packets_remote = zp.read_packets_csv(remote)
        df = zp.merge_packet_dfs(df_packets_local, df_packets_remote)
        packets.append(df)
        packets_local.append(df_packets_local)
        packets_remote.append(df_packets_remote)

        frames_local.append(zp.read_frames_csv(local))
        frames_remote.append(zp.read_frames_csv(remote))


    packets = pd.concat(packets)
    packets_local = pd.concat(packets_local)
    packets_remote = pd.concat(packets_remote)
    streams = pd.concat(streams)
    frames_local = pd.concat(frames_local)
    frames_remote = pd.concat(frames_remote)

    # packets
    owd_ul = []
    owd_dl = []

    tput_total_ul = []
    tput_total_dl = []
    tput_video_ul = []
    tput_video_dl = []
    tput_fec_ul = []
    tput_fec_dl = []

    gput_total_ul = []
    gput_total_dl = []
    gput_video_ul = []
    gput_video_dl = []
    gput_fec_ul = []
    gput_fec_dl = []

    # frames
    fps_ul = [] # packets sent from local and frames displayed on remote
    fps_dl = []

    jitter_ul = [] # packets sent from local and frames displayed on remote, unit=ms
    jitter_dl = []

    def comp_rate(packets_ssrc): # key = pl_len, pl_len_local, pl_len_remote
        return packets_ssrc.set_index("ts")["pl_len"].resample("1s").sum() * 8 / 1e6

    for stream in streams.itertuples():
        packets_owd = abs(packets[packets.ssrc == stream.rtp_ssrc].owd)
        packets_local_ssrc = packets_local[packets_local.ssrc == stream.rtp_ssrc]
        packets_remote_ssrc = packets_remote[packets_remote.ssrc == stream.rtp_ssrc]
        frames_local_ssrc = frames_local[frames_local.ssrc == stream.rtp_ssrc]
        frames_remote_ssrc = frames_remote[frames_remote.ssrc == stream.rtp_ssrc]
        if not(stream.media_type == "v" and stream.stream_type == "m"):
            continue

        rate_local_total = comp_rate(packets_local_ssrc)
        rate_local_video = comp_rate(packets_local_ssrc[packets_local_ssrc.pt == 98])
        rate_local_fec = comp_rate(packets_local_ssrc[packets_local_ssrc.pt == 110])
        rate_remote_total = comp_rate(packets_remote_ssrc)
        rate_remote_video = comp_rate(packets_remote_ssrc[packets_remote_ssrc.pt == 98])
        rate_remote_fec = comp_rate(packets_remote_ssrc[packets_remote_ssrc.pt == 110])

        if stream.is_local:
            owd_ul.extend(packets_owd)
            fps_ul.extend(frames_remote_ssrc.fps)
            jitter_ul.extend(frames_remote_ssrc.jitter_ms)
            tput_total_ul.extend(rate_local_total)
            tput_video_ul.extend(rate_local_video)
            tput_fec_ul.extend(rate_local_fec)
            gput_total_ul.extend(rate_remote_total)
            gput_video_ul.extend(rate_remote_video)
            gput_fec_ul.extend(rate_remote_fec)
        else:
            owd_dl.extend(packets_owd)
            fps_dl.extend(frames_local_ssrc.fps)
            jitter_dl.extend(frames_local_ssrc.jitter_ms)
            tput_total_dl.extend(rate_remote_total)
            tput_video_dl.extend(rate_remote_video)
            tput_fec_dl.extend(rate_remote_fec)
            gput_total_dl.extend(rate_local_total)
            gput_video_dl.extend(rate_local_video)
            gput_fec_dl.extend(rate_local_fec)

    stats = [("owd_ms_ul", owd_ul),
             ("owd_ms_dl", owd_dl),

             ("tput_total_mbps_ul", tput_total_ul),
             ("tput_total_mbps_dl", tput_total_dl),
             ("tput_video_mbps_ul", tput_video_ul),
             ("tput_video_mbps_dl", tput_video_dl),
             ("tput_fec_mbps_ul", tput_fec_ul),
             ("tput_fec_mbps_dl", tput_fec_dl),

             ("gput_total_mbps_ul", gput_total_ul),
             ("gput_total_mbps_dl", gput_total_dl),
             ("gput_video_mbps_ul", gput_video_ul),
             ("gput_video_mbps_dl", gput_video_dl),
             ("gput_fec_mbps_ul", gput_fec_ul),
             ("gput_fec_mbps_dl", gput_fec_dl),

             ("fps_ul", fps_ul),
             ("fps_dl", fps_dl),
             ("jitter_ms_ul", jitter_ul),
             ("jitter_ms_dl", jitter_dl)]
    labels, metrics = zip(*stats)
    bxp_stats = boxplot_stats(metrics, labels=labels)

    for idx in range(len(bxp_stats)):
        label = bxp_stats[idx]["label"]
        data = [arr for (key, arr) in stats if key == label][0]
        bxp_stats[idx]["stddev"] = np.std(data)
        bxp_stats[idx]["min"] = np.min(data) if len(data) > 0 else np.nan
        bxp_stats[idx]["max"] = np.max(data) if len(data) > 0 else np.nan

    # Remove fliers
    for idx in range(len(bxp_stats)):
        bxp_stats[idx]["fliers"] = []

    return bxp_stats

# def replace_label(ty, label):
#     if "_ul" in label:
#         return f"{ty.upper()}\nUL"
#     if "_dl" in label:
#         return f"{ty.upper()}\nDL"
#     return label

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def replace_label(stats):
    if "label" not in stats:
        return stats
    if "_ul" in stats["label"]:
        stats["label"] = "UL"
    elif "_dl" in stats["label"]:
        stats["label"] = "DL"
    return stats

def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("directories", nargs="+", help="Directories with zpkt and parsed csv files")
    parser.add_argument("--stl", nargs="+", help="Directories with 'local' and remote folders that contain local zpkt and parsed csv files")
    parser.add_argument("--ter", nargs="*", help="Directories with 'local' and remote folders that contain local zpkt and parsed csv files")
    parser.add_argument("--save", help="Write plot to this file")
    parser.add_argument("--csv", help="Write metrics to this path prefix")
    parser.add_argument("-b", action="store_true", help="Break after parsing csvs")
    args = parser.parse_args()

    if args.stl is None:
        parser.print_help()
        sys.exit(1)

    print(f"Parsing stl...")
    bxp_stl = compute_bxp_metrics(args.stl)
    print(f"Parsing ter...")
    bxp_ter = compute_bxp_metrics(args.ter) if args.ter else []

    if args.csv:
        filepath, ext = os.path.splitext(args.csv)
        with open(filepath + "_stl" + ext, "w") as f:
            json.dump(bxp_stl, f, indent=2, cls=NpEncoder)
        with open(filepath + "_ter" + ext, "w") as f:
            json.dump(bxp_ter, f, indent=2, cls=NpEncoder)
        return

    print(f"Plotting...")

    plt.set_cmap("tab10")
    rcParams["font.family"] = "CMU Sans Serif"
    rcParams["font.size"] = 9.0
    plt.rc('text', usetex=True)

    fig, axes = plt.subplots(figsize=(4, 1.5), ncols=3)

    # facecolor=cols[0], lw=1), medianprops=dict(color="yellow")
    colors = plt.get_cmap("tab10").colors

    stl_boxprops = dict(lw=1, facecolor=colors[0])
    ter_boxprops = dict(lw=1, facecolor=colors[1])
    medianprops = dict(color="yellow")
    stl_props = dict(boxprops=stl_boxprops, medianprops=medianprops, positions=[0.5,1.5], widths=0.4, patch_artist=True)
    ter_props = dict(boxprops=ter_boxprops, medianprops=medianprops, positions=[0.9,1.9], widths=0.4, patch_artist=True)

    stl_stats = [replace_label(s) for s in bxp_stl if s["label"].startswith("owd")]
    ter_stats = [replace_label(s) for s in bxp_ter if s["label"].startswith("owd")]
    axes[0].bxp(stl_stats, **stl_props)
    axes[0].bxp(ter_stats, **ter_props)
    axes[0].set_xticks([0.7, 1.7], ["UL", "DL"])
    axes[0].set_ylabel("OWD (ms)")

    stl_stats = [replace_label(s) for s in bxp_stl if s["label"].startswith("rate")]
    ter_stats = [replace_label(s) for s in bxp_ter if s["label"].startswith("rate")]
    axes[1].bxp(stl_stats, **stl_props)
    axes[1].bxp(ter_stats, **ter_props)
    axes[1].set_xticks([0.7, 1.7], ["UL", "DL"])
    axes[1].set_ylabel("Bitrate (Mbps)")

    stl_stats = [replace_label(s) for s in bxp_stl if s["label"].startswith("fps")]
    ter_stats = [replace_label(s) for s in bxp_ter if s["label"].startswith("fps")]
    axes[2].bxp(stl_stats, **stl_props)
    axes[2].bxp(ter_stats, **ter_props)
    axes[2].set_xticks([0.7, 1.7], ["UL", "DL"])
    axes[2].set_ylabel("FPS")

    # stl_stats = [replace_label(s) for s in bxp_stl if s["label"].startswith("jitter")]
    # ter_stats = [replace_label(s) for s in bxp_ter if s["label"].startswith("jitter")]
    # axes[3].bxp(stl_stats, **stl_props)
    # axes[3].bxp(ter_stats, **ter_props)
    # axes[3].set_xticks([0.7, 1.7], ["UL", "DL"])
    # axes[3].set_ylabel("Frame Jitter (ms)")

    # axes[0].legend(ncol=2, handles=[
    #     mpatches.Patch(color="green", label='Starlink'),
    #     mpatches.Patch(color="red", label='Terrestrial')])


    parts = [
        mpatches.Patch(color=colors[0], label='Starlink'),
        mpatches.Patch(color=colors[1], label='Terrestrial')
    ]
    fig_legend = plot_external_legend(parts, (4, 1), ncols=3)
                                      # labelspacing=0.3, handlelength=1.2, handletextpad=0.4, columnspacing=1.2)

    fig.tight_layout()
    fig.subplots_adjust(wspace=0.6)

    # if args.save:
    #     plt.savefig(args.w, bbox_inches="tight", pad_inches=0)
    # else:
    #     print("Continue to show plot...")
    #     breakpoint()
    #     plt.show()


    if args.save:
        filepath, ext = os.path.splitext(args.save)
        if ext == ".pdf":
            with PdfPages(args.save) as pdf:
                pdf.savefig(fig, bbox_inches="tight", pad_inches=0)
                pdf.savefig(fig_legend, bbox_inches="tight")
                            # bbox_inches=Bbox([[0.1,0], [4,4]]))
                            #
        else:
            fig.savefig(filepath + "_plot" + ext, bbox_inches="tight", pad_inches=0)
            fig_legend.savefig(filepath + "_legend" + ext, bbox_inches="tight")
    else:
        print("Continue to show plot...")
        breakpoint()
        plt.show()


if __name__ == "__main__":
    main()

#
# media_type = (a)udio, (v)ideo, (s)creen
# stream_type = (f)ec or (m)edia
#
#
# packets.csv
# flow_type =
