#!/usr/bin/env python3

import argparse
import json
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
from matplotlib.backends.backend_pdf import PdfPages
import shutil

def plot_optimization_interval(ax, start, end):
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
    for opt in res:
        part = ax.axvline(opt, label="SL Interval",
                          # color="green", alpha=0.5,
                          color="#360B18", alpha=1,
                          linestyle="--", zorder=-1)
    return part

def datetime_as_timedelta_formatter(start_ts):
    start_mts = mdates.date2num(start_ts)
    def formatter(x, pos):
        diff = mdates.num2timedelta(x - start_mts).total_seconds()
        return f"{diff:g}"
    return formatter

def plot_external_legend(parts, figsize, **kwargs): # ncol =
    fig_legend = plt.figure(figsize=figsize)
    fig_legend.legend(parts, [p.get_label() for p in parts], **kwargs)
    fig_legend.tight_layout()
    return fig_legend


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dirs", nargs="+", help="Result directories")
    parser.add_argument("--gdelays", nargs="+", help="delay_ts files")
    parser.add_argument("--views", nargs="+", help="Parts to show, in second offsets: start,end")
    parser.add_argument("--save", help="Save datapoints to csv file")
    args = parser.parse_args()

    if len(args.dirs) != len(args.gdelays) != len(args.views):
        print("The same number of arguments need to be passed")
        sys.exit(1)
    args.views = [(int(view.split(",")[0]), int(view.split(",")[1])) for view in args.views]

    plt.set_cmap("tab10")
    rcParams["font.family"] = "CMU Sans Serif"
    rcParams["font.size"] = 10.0
    plt.rc('text', usetex=True if shutil.which('latex') else False)


    fig, axes = plt.subplots(figsize=(4, 1.5), ncols=len(args.dirs), sharey=True)


    for ax_i, (ax, dir, delays_ts, view) in enumerate(zip(axes, args.dirs, args.gdelays, args.views)):
        with open(os.path.join(dir, "current_rtt.json"), "r") as f:
            rtt = json.load(f)
            rtt["ts"] = [pd.Timestamp(v, unit="s") for v in rtt["ts"]]
        with open(os.path.join(dir, "parsed_videoReceiveStream.json"), "r") as f:
            video = json.load(f)
            video = video[list(video.keys())[0]]
            video["ts"] = [pd.Timestamp(v, unit="s") for v in video["time_ms"]]

        parts = []

        colors = list(plt.get_cmap("tab10").colors)

        start_ts, end_ts = rtt["ts"][0], rtt["ts"][-1]

        parts.append(ax.plot(rtt["ts"], rtt["rtts"], label="RTT", color=colors.pop(0))[0])

        ax_fps = ax.twinx()

        color_fps = colors.pop(0)
        ax_fps.yaxis.label.set_color(color_fps)
        ax_fps.spines['right'].set_color(color_fps)
        ax_fps.tick_params(axis="y", color=color_fps)

        parts.append(ax_fps.plot(video["ts"], video["ren_fps"], label="FPS", color=color_fps)[0])
        colors.pop(0) # skip green; use by axvline
        parts.append(ax.plot(video["ts"], video["jb_delay"], label="Jitter Buffer", color=colors.pop(0))[0])

        gdelay = pd.read_csv(delays_ts)
        gdelay["ts"] = pd.to_datetime(gdelay["ts"], unit="s")
        gdelay = gdelay[(gdelay.ts >= start_ts) & (gdelay.ts <= end_ts)]

        parts.append(ax.scatter(gdelay["ts"], gdelay["delay_ms"], label="Game Delay", color=colors.pop(0)))

        print(f"dir={dir}")
        if dir.find("starlink") > 0:
            plot_optimization_interval(ax, start_ts, end_ts)

        if view[0] != 0:
            ax.set_xlim(left=start_ts + pd.Timedelta(view[0], unit="seconds"))
        if view[1] != 0:
            ax.set_xlim(right=start_ts + pd.Timedelta(view[1], unit="seconds"))

        ax_fps.set_ylim(40, 65)
        ax.set_ylim(0, 220)
        ax.set_yticks([0, 50, 100, 150, 200])
        if ax_i == 0:
            ax.set_ylabel("ms")
        if ax_i == len(axes)-1:
            ax_fps.set_ylabel("FPS") # last column
        else:
            ax_fps.get_yaxis().set_ticklabels([])
        ax.set_xlabel("Time (s)")

        xfmt = datetime_as_timedelta_formatter(start_ts.replace(microsecond=0, nanosecond=0))
        ax.xaxis.set_major_formatter(xfmt)

        xtick_interval = 10
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=xtick_interval))

        # Draw ax above ax_fps in terms of zorder
        ax.set_zorder(1)
        ax.set_frame_on(False)

    fig.tight_layout()

    fig.subplots_adjust(wspace=0.1)

    fig_legend = plot_external_legend(parts, (4, 1), ncols=len(parts),
                                      labelspacing=0.3, handlelength=1.2, handletextpad=0.4, columnspacing=1.2)

    if args.save:
        filepath, ext = os.path.splitext(args.save)
        if ext == ".pdf":
            with PdfPages(args.save) as pdf:
                pdf.savefig(fig, bbox_inches="tight", pad_inches=0)
                pdf.savefig(fig_legend, bbox_inches="tight")
        else:
            fig.savefig(filepath + "_plot" + ext, bbox_inches="tight", pad_inches=0)
            fig.savefig(filepath + "_legend" + ext, bbox_inches="tight")
    else:
        plt.show()

if __name__ == "__main__":
    main()
