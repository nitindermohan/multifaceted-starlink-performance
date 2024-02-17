#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages
import os.path
import argparse
import sys
import shutil

import zoom_parser as zp

def plot_external_legend(parts, figsize, **kwargs): # ncol =
    fig_legend = plt.figure(figsize=figsize)
    fig_legend.legend(parts, [p.get_label() for p in parts], **kwargs)
    fig_legend.tight_layout()
    return fig_legend

def compute_interval_timestamps(ax, start, end):
    res = []
    opt_secs = [12,27,42,57]
    tmp = start.replace(second=opt_secs[0])
    for opt_sec in opt_secs:
        if opt_sec >= start.second:
            tmp = start.replace(second=opt_sec)
            break
    tmp = tmp.replace(microsecond=0, nanosecond=0)
    res.append(tmp)
    while True:
        tmp += pd.Timedelta(seconds=15)
        if tmp > end:
            break
        else:
            res.append(tmp)
    return res

def plot_latency(ax, streams, df): # df = packets
    media_streams = streams[(streams.stream_type == "m") & (streams.media_type == "v")]

    for stream in media_streams.itertuples():
        df_ssrc = df[(df.ssrc == stream.rtp_ssrc)]

        direction = "UL" if stream.is_local else "DL"
        media_type = "Audio" if stream.media_type == "a" else "Video" if stream.media_type == "v" else stream.media_type
        # ax.plot(df_ssrc['ts_local'], abs(df_ssrc['owd']), label=f"{direction} {media_type}")
        ax.scatter(df_ssrc['ts_local'], abs(df_ssrc['owd']), label=f"{direction} {media_type}",
                   s=0.3, rasterized=True)

ctab = list(plt.get_cmap("tab10").colors)
colors = dict(owd=ctab[0], video=ctab[1], fec=ctab[3],
              interval="#360B18")
              # interval=ctab[2])

def plot(ax, dir_path, view, plot_intervals=False):
    dir_local = os.path.join(dir_path, "local/")
    dir_remote = os.path.join(dir_path, "remote/")

    try:
        packets_local = zp.read_packets_csv(dir_local)
        packets_remote = zp.read_packets_csv(dir_remote)
        packets = zp.merge_packet_dfs(packets_local, packets_remote)

        # lost = zp.find_lost_packets(packets_local, packets_remote)

        # frames_local = zp.read_frames_csv(dir_local)
        # frames_remote = zp.read_frames_csv(dir_remote)

        streams = zp.read_streams_csv(dir_local)

        # stats_local = read_stats_csv(dir_local)
        # stats_remote = read_stats_csv(dir_remote)
        # stats_fig(streams, stats_local, stats_remote)
    except Exception as e:
        print(f"Failed to parse Zoom packet data from {dir_path}: {e}")
        sys.exit(1)


    media_only = streams.stream_type == "m"
    video_only = streams.media_type == "v"
    uplink_only = (streams.is_local)
    media_streams = streams[media_only & video_only & uplink_only]

    ax2 = ax.twinx()

    def comp_rate(df):
        return df.set_index("ts_rel")["pl_len"].resample("1s").sum() * 8 / 1e6

    for stream in media_streams.itertuples():
        owd = abs(packets[(packets.ssrc == stream.rtp_ssrc)].set_index("ts").owd)
        packets_local_ssrc = packets_local[packets_local.ssrc == stream.rtp_ssrc]

        direction = "UL" if stream.is_local else "DL"
        media_type = "Audio" if stream.media_type == "a" else "Video" if stream.media_type == "v" else stream.media_type
        # color = colors[0] if direction == "UL" else colors[3]

        # ax.scatter(df.ts.dt.total_seconds(), abs(df.owd),
        ax2.scatter(owd.index.total_seconds(), owd, label=f"{direction} {media_type}",
                    color=colors["owd"], s=0.3, rasterized=True,
                    zorder=-1)

        video_bitrate = comp_rate(packets_local_ssrc[packets_local_ssrc.pt == 98])
        fec_bitrate = comp_rate(packets_local_ssrc[packets_local_ssrc.pt == 110])
        ax.plot(video_bitrate.index.total_seconds(), video_bitrate,
                label=f"{direction} {media_type} Video", color=colors["video"])
        ax.plot(fec_bitrate.index.total_seconds(), fec_bitrate,
                label=f"{direction} {media_type} FEC", color=colors["fec"])

    if plot_intervals:
        opt_tss = compute_interval_timestamps(ax, min(packets.ts_local), max(packets.ts_local))
        min_ts = min(packets.ts_local)
        for opt in opt_tss:
            xval = (opt - min_ts).total_seconds()
            part = ax2.axvline(xval, label="SL Interval", color=colors["interval"],
                               alpha=1, linestyle="--", zorder=-2)

    ax.set_ylabel("Mbps")
    # ax.yaxis.label.set_color(colors[1])
    # ax.spines['right'].set_color(colors[1])
    # ax.tick_params(axis="y", color=colors[1])
    ax.set_ylim(0, 1.5)

    ax2.set_ylabel("Latency (ms)")
    ax2.yaxis.label.set_color(colors["owd"])
    ax2.spines['left'].set_color(colors["owd"])
    ax2.tick_params(axis="y", color=colors["owd"])
    ax2.set_ylim(0, 150)

    # Layer ax over ax2
    ax.set_zorder(1)
    ax.set_frame_on(False)

    ax.set_xlabel("Time (s)")
    if view is not None:
        ax.set_xlim(left=view[0], right=view[1])

def parse_int_tuple(arg):
    if arg is None:
        return None
    parts = arg.split(",")
    return (int(parts[0]), int(parts[1]))

def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("directories", nargs="+", help="Directories with zpkt and parsed csv files")
    parser.add_argument("ter", help="Terrestrial: directories with local/ and remote/ directories that contain zpkt and parsed csv files")
    parser.add_argument("stl", help="Starlink: directories with local/ and remote/ directories that contain zpkt and parsed csv files")
    parser.add_argument("--view-ter", help="Part of stl to show, seconds offsets: start,end")
    parser.add_argument("--view-stl", help="Part of stl to show, seconds offsets: start,end")
    parser.add_argument("-b", action="store_true", help="Break after parsing csvs")
    parser.add_argument("--save", "-w", help="Write plot")
    args = parser.parse_args()

    view_stl = parse_int_tuple(args.view_stl)
    view_ter = parse_int_tuple(args.view_ter)

    plt.set_cmap("tab10")
    rcParams["font.family"] = "CMU Sans Serif"
    rcParams["font.size"] = 10.0
    plt.rc('text', usetex=True if shutil.which('latex') else False)

    if args.b:
        breakpoint()

    fig, axes = plt.subplots(figsize=(4,1.1), ncols=2, dpi=300, sharey=True)

    plot(axes[0], args.ter, view_ter)
    plot(axes[1], args.stl, view_stl, plot_intervals=True)

    twin_ax_0 = axes[0].get_shared_x_axes().get_siblings(axes[0])[0]
    twin_ax_1 = axes[1].get_shared_x_axes().get_siblings(axes[0])[0]
    twin_ax_0.set_ylabel("")
    twin_ax_0.set_yticklabels([])
    axes[1].set_ylabel("")

    axes[0].xaxis.set_major_locator(mticker.MultipleLocator(base=15))
    axes[1].xaxis.set_major_locator(mticker.MultipleLocator(base=15))

    fig.subplots_adjust(wspace=0.1)

    # twin_ax_1.get_shared_y_axes().join(twin_ax_0, twin_ax_1)

    # fig.subplots_adjust(wspace=0.1)

    parts = [
        mpatches.Patch(color=colors["owd"], label="One-Way Delay"),
        mpatches.Patch(color=colors["video"], label="Video Throughput"),
        mpatches.Patch(color=colors["fec"], label="FEC Throughput")
        # mpatches.Patch(color=colors["interval"], label='SL')
    ]
    fig_legend = plot_external_legend(parts, (4, 1), ncols=len(parts))

    if args.save:
        filepath, ext = os.path.splitext(args.save)
        if ext == ".pdf":
            with PdfPages(args.save) as pdf:
                pdf.savefig(fig, bbox_inches="tight", pad_inches=0)
                pdf.savefig(fig_legend, bbox_inches="tight")
        else:
            # fig.savefig(args.save, bbox_inches="tight", pad_inches=0)
            fig.savefig(filepath + "_plot" + ext, bbox_inches="tight", pad_inches=0)
            fig_legend.savefig(filepath + "_legend" + ext, bbox_inches="tight")
    else:
        plt.show()

if __name__ == "__main__":
    main()
