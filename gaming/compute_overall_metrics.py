#!/usr/bin/env python3

import argparse
import json
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

import compute_delay

def compute_overall(args):
    metrics = dict(
        current_delay = [],
        jb_delay = [],
        decode_delay = [],
        render_delay_ms = [],
        gaming_delay = [],
        rtt = [],
        ren_fps = [],
        freeze_count = 0,
        total_freezes_duration_ms = 0,
        frame_drop = 0,
        height = {1080:0, 720:0},
        rtx_bps = [],
        rx_bps = [],
        target_delay_ms = [],
        interframe_delay_max_ms = [],
        interframe_delay_ms = [],
        duration_s = 0,
        frames_rendered = 0
    )

    for d in args.directories:
        with open(os.path.join(d, "parsed_videoReceiveStream.json"), "r") as f:
            stats = json.load(f)
            stats = stats[list(stats.keys())[0]]
            # dict_keys(['count', 'current_delay', 'dec_fps', 'decode_delay', 'first_frame_received_to_decoded_ms', 'frame_drop', 'frames_decoded', 'frames_rendered', 'freeze_count', 'height', 'interframe_delay_max_ms', 'jb_cuml_delay', 'jb_delay', 'jb_emit_count', 'max_decode_ms', 'min_playout_delay_ms', 'net_fps', 'pause_count', 'ren_fps', 'render_delay_ms', 'rtx_bps', 'rx_bps', 'sum_squared_frame_durations', 'sync_offset_ms', 'target_delay_ms', 'time_ms', 'total_bps', 'total_decode_time_ms', 'total_frames_duration_ms', 'total_freezes_duration_ms', 'total_inter_frame_delay', 'total_pauses_duration_ms', 'total_squared_inter_frame_delay', 'width'])

        for metric in metrics.keys():
            if metric in ["gaming_delay", "rtt"]:
                pass
                # computed later
            elif metric in ["freeze_count", "total_freezes_duration_ms", "frame_drop"]:
                # These values only increase
                metrics[metric] += np.max(stats[metric])
            elif metric == "height":
                    values, counts = np.unique(stats[metric], return_counts=True)
                    for val, cnt in zip(values, counts):
                        metrics[metric][int(val)] += cnt
            elif metric == "duration_s":
                metrics[metric] += np.max(stats["time_ms"]) - np.min(stats["time_ms"])
            elif metric == "frames_rendered":
                metrics[metric] += np.max(stats[metric]) - np.min(stats[metric])
            elif metric == "interframe_delay_ms":
                stats_key = "total_inter_frame_delay"
                metrics[metric] = [(a-b)*1000 for a,b in zip(stats[stats_key][1:], stats[stats_key][:-1])]
            else:
                metrics[metric].extend(stats[metric])

        gd_df = compute_delay.assemble_df(d)
        gdelay = compute_delay.compute_delay(gd_df)
        metrics["gaming_delay"].extend(gdelay.to_list())

        with open(os.path.join(d, "current_rtt.json"), "r") as f:
            rtts = json.load(f)
            metrics["rtt"].extend(rtts["rtts"])

    result = dict()
    for metric, data in metrics.items():
        if metric in ["freeze_count"]:
            result[metric] = data
        elif metric == "total_freezes_duration_ms":
            result[metric] = data
            result[metric + "_rel"] = float(data / (metrics["duration_s"] * 1000))
        elif metric == "frame_drop":
            result[metric] = data
            result[metric + "_rel"] = float(data / (data + metrics["frames_rendered"]))
        elif metric == "height":
            total = data[1080] + data[720]
            result["height_1080"] = int(data[1080])
            result["height_1080_rel"] = data[1080] / total
            result["height_720"] = int(data[720])
            result["height_720_rel"] = data[720] / total
        elif metric == "duration_s":
            result[metric] = data
        elif metric == "frames_rendered":
            result[metric] = int(data)
        else:
            result[metric] = dict(
                mean=np.mean(data),
                std=np.std(data),
                median=np.percentile(data, 50),
                min=np.min(data),
                max=np.max(data),
                cnt=len(data),
                coeff_var=np.std(data) / np.mean(data)
            )

    for k,v in result.items():
        print(f"{k}:{type(v)}")

    print(json.dumps(result, indent=4))
    if args.save:
        with open(args.save, "w") as f:
            json.dump(result, f, indent=4)


def compute_metrics(df):
    return dict(mean=df.mean(),
                std=df.std(),
                median=df.median(),
                min=df.min(),
                max=df.max(),
                cnt=len(df),
                coeff_var=df.std() / df.mean())

def compute_per_minute(args):
    metrics = dict(
        ren_fps = "mean",
        jb_delay = "mean",
        current_delay = "mean",
        decode_delay = "mean",
        render_delay_ms = "mean",
        freeze_count = "diff",
        total_freezes_duration_ms = "diff",
        frame_drop = "diff",
        # height = {1080:0, 720:0},
        rtx_bps = "mean",
        rx_bps = "mean",
        target_delay_ms = "mean",
        interframe_delay_max_ms = "mean",
        # duration_s = 0,
        frames_rendered = "" # do nothing
    )

    dfs = []
    rtts = []
    gdelays = []
    for di, d in enumerate(args.directories):
        print(d)
        with open(os.path.join(d, "parsed_videoReceiveStream.json"), "r") as f:
            stats = json.load(f)
            stats = stats[list(stats.keys())[0]]
            # dict_keys(['count', 'current_delay', 'dec_fps', 'decode_delay', 'first_frame_received_to_decoded_ms', 'frame_drop', 'frames_decoded', 'frames_rendered', 'freeze_count', 'height', 'interframe_delay_max_ms', 'jb_cuml_delay', 'jb_delay', 'jb_emit_count', 'max_decode_ms', 'min_playout_delay_ms', 'net_fps', 'pause_count', 'ren_fps', 'render_delay_ms', 'rtx_bps', 'rx_bps', 'sum_squared_frame_durations', 'sync_offset_ms', 'target_delay_ms', 'time_ms', 'total_bps', 'total_decode_time_ms', 'total_frames_duration_ms', 'total_freezes_duration_ms', 'total_inter_frame_delay', 'total_pauses_duration_ms', 'total_squared_inter_frame_delay', 'width'])

        selected_stats = {k:v for k,v in stats.items() if k in metrics.keys()}
        df = pd.DataFrame.from_dict(selected_stats)
        df.set_index(pd.to_datetime(stats["time_ms"], unit="s"), inplace=True)
        df["file"] = di

        total_ifd = stats["total_inter_frame_delay"]
        df["interframe_delay_ms"] = [np.nan] + [(a-b)*1000 for a,b in zip(total_ifd[1:], total_ifd[:-1])]
        metrics["interframe_delay_ms"] = "mean"

        dfs.append(df)

        # for metric in metrics.keys():
        #     metrics[metric].extend(stats[metric])

        gd_df = compute_delay.assemble_df(d)
        gdelay = compute_delay.compute_delay(gd_df)
        gdelays.append(gdelay)

        with open(os.path.join(d, "current_rtt.json"), "r") as f:
            rtt_stats = json.load(f)
            rtt_df = pd.DataFrame(rtt_stats["rtts"], index=pd.to_datetime(rtt_stats["ts"], unit="s"))
            rtts.append(rtt_df)

    df = pd.concat(dfs).sort_index()
    dfr = df.resample("60s")
    test_gap_mask = ~dfr.file.max().isna()
    dfr_mean = dfr.mean()[test_gap_mask]
    dfr_max = dfr.max()[test_gap_mask]

    df_diff = dfr_max - dfr_max.shift(1).fillna(0)
    # reset counters back to zero on file changes
    mask = dfr_max["file"] != dfr_max["file"].shift(1)
    df_diff[mask] = 0

    # frame_drop relative: (df_diff["frame_drop"] / (df_diff["frames_rendered"] + df_diff["frame_drop"])).describe()

    result = dict()
    for metric, how in metrics.items():
        if how == "mean":
            result[metric] = compute_metrics(dfr_mean[metric])
        if how == "diff":
            result[metric] = compute_metrics(df_diff[metric])

    dfrtt = pd.concat(rtts).sort_index()
    dfrtt_mean = dfrtt.resample("60s").mean()
    result["rtt"] = compute_metrics(dfrtt_mean[0])

    dfg = pd.concat(gdelays).sort_index()
    dfg_mean = dfg.resample("60s").mean()
    result["gaming_delay"] = compute_metrics(dfg_mean)

    freeze_occurences = df_diff[df_diff["total_freezes_duration_ms"] > 0]["total_freezes_duration_ms"]
    result["freeze_occurences"] = compute_metrics(freeze_occurences)

    drop_occurences = df_diff[df_diff["frame_drop"] > 0]["frame_drop"]
    result["frame_drop_occurences"] = compute_metrics(drop_occurences)

    # for k,v in result.items():
    #     print(f"{k}:{type(v)}")

    print(json.dumps(result, indent=4))
    if args.save:
        with open(args.save, "w") as f:
            json.dump(result, f, indent=4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+", help="Result directories")
    parser.add_argument("--method", choices=["per_minute", "overall"], default="per_minute", help="How to group data points")
    parser.add_argument("--save", help="Save datapoints to csv file")
    args = parser.parse_args()

    if args.method == "per_minute":
        compute_per_minute(args)
    else:
        compute_overall(args)


if __name__ == "__main__":
    main()
