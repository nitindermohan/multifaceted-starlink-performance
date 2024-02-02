#!/usr/bin/env python3

import argparse
import json
import pandas as pd
import numpy as np
import os
import sys

def compute_blocks(ls):
    blocks = []
    block_start = None
    prev = None
    ls = sorted([int(v) for v in ls])
    for cur in sorted(ls):
        if block_start is None:
            block_start = cur
        if prev is not None:
            if prev + 1 != cur:
                blocks.append((block_start, prev))
                block_start = cur
        prev = cur
    return blocks

def assemble_df(base_path):
    action_frame_ts = os.path.join(base_path, "frame_timestamps.json")
    bot_log = os.path.join(base_path, "bot_log.csv")

    with open(action_frame_ts) as f:
        frame_tss = json.load(f)

    action_frame_ts = []
    action_frames = compute_blocks(frame_tss.keys())
    for (start, _) in action_frames:
        try:
            frame_ts = frame_tss[str(start)][1]
            if frame_ts == "skipped":
                continue
            ts = pd.Timestamp(frame_ts, unit="s")
        except:
            print(f"Failed to convert {start}")
            breakpoint()
        action_frame_ts.append((ts, "action", start))

    cmds = []
    with open(bot_log) as f:
        for line in f.readlines():
            ts, cmd = line.strip().split(",")
            cmds.append((pd.Timestamp(int(ts)), cmd, None))

    columns = ["ts", "event", "frame"]
    df1 = pd.DataFrame(action_frame_ts, columns=columns)
    df2 = pd.DataFrame(cmds, columns=columns)
    df = pd.concat([df1, df2]).set_index("ts").sort_index()
    df["delay_ms"] = np.nan
    return df

def compute_delay(df):
    ts_triggers = df[(df.event == "s") | (df.event == "r")].index
    for cmd_ts in ts_triggers:
        next_event = df[(df.index > cmd_ts) & (df.event == "action")]
        if len(next_event) == 0:
            continue
        next_event = next_event.iloc[0]
        action_ts = next_event.name
        action_delay = (action_ts - cmd_ts).total_seconds() * 1000
        if action_delay > 500:
            print(f"Discarded large delay of {action_delay:.0f} ms at {action_ts} / frame {next_event.frame}", file=sys.stderr)
            continue
        if action_delay < 30:
            print(f"Discarded small delay of {action_delay:.0f} ms at {action_ts} / frame {next_event.frame}", file=sys.stderr)
            # print(df[(df.index >= (cmd_ts - pd.Timedelta(seconds=1)))])
            continue
        df.loc[cmd_ts, "delay_ms"] = action_delay
    return df.dropna(subset="delay_ms")["delay_ms"]# .to_list()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+", help="Result directories")
    parser.add_argument("--save", help="Save datapoints to csv file")
    parser.add_argument("--savets", help="Save datapoints and timestamps to csv file")
    args = parser.parse_args()

    tss = []
    delays = []
    for d in args.directories:
        print(d, file=sys.stderr)
        df = assemble_df(d)
        delay = compute_delay(df)
        tss.extend(delay.index.to_list())
        delays.extend(delay.to_list())

    result = dict(
        min=min(delays),
        q1=np.percentile(delays, 25),
        med=np.percentile(delays, 50),
        q3=np.percentile(delays, 75),
        max=max(delays),
        count=len(delays))
    print(result)

    if args.save:
        with open(args.save, "w") as f:
            for d in delays:
                f.write(f"{d:.2f}")
                f.write("\n")
    if args.savets:
        with open(args.savets, "w") as f:
            f.write("ts,delay_ms\n")
            for ts, d in zip(tss, delays):
                f.write(f"{ts.timestamp()},{d:.2f}\n")

    # desc = df.dropna(subset="delay_ms")["delay_ms"].describe()
    # print(desc)
    # print(df.dtypes)



if __name__ == "__main__":
    main()
