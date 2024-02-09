#!/usr/bin/env python3

import pandas as pd
import os.path

LOCAL_IP_PREFIXES = ["192.168", "131.159"]

def read_packets_csv(directory):
    df = pd.read_csv(os.path.join(directory, "packets.csv"))
    df.rename(columns={'#ts_s':'ts_s'}, inplace=True)
    df['ts'] = pd.to_datetime((df['ts_s']*1e6 + df['ts_us']) / 1e6, unit="s")
    df['ts_rel'] = df.ts - df.ts.min()
    return df

def merge_packet_dfs(local, remote, join="inner"):   #
    # cols = ['media_type','pkts_in_frame','ssrc','pt','rtp_seq','rtp_ts','pl_len','rtp_ext1','drop']
    cols = ["ssrc", "rtp_seq", "rtp_ts", "pt"]
    m = local.merge(remote, on=cols, how=join, suffixes=('_local', '_remote'))
    m['owd'] = ((m['ts_s_local']*1e6 + m['ts_us_local']) - (m['ts_s_remote']*1e6 + m['ts_us_remote'])) / 1e3
    min_ts = min(m['ts_local'])
    m['ts'] = m['ts_local'] - min_ts
    return m

def find_lost_packets(local, remote):
    df = merge_packet_dfs(local, remote, join="left")
    # pt 98 are video packets. pt=110 are FEC packets that are only sent, processed by the server, and never received.
    df = df[(df.ts_s_remote.isna()) & (df.pt == 98)]#(df.pt_local == 98)]
    return df

def read_streams_csv(directory):
    df = pd.read_csv(os.path.join(directory, "streams.csv"))
    df["is_local"] = df.ip_src.apply(ip_is_local)
    return df

def read_frames_csv(directory):
    df = pd.read_csv(os.path.join(directory, "frames.csv"))
    df.rename(columns={' min_ts_us':'min_ts_us'}, inplace=True)
    df["min_ts"] = pd.to_datetime((df.min_ts_s * 1e6 + df.min_ts_us) / 1e6, unit="s")
    df["max_ts"] = pd.to_datetime((df.max_ts_s * 1e6 + df.max_ts_us) / 1e6, unit="s")
    df["is_local"] = df.ip_src.apply(ip_is_local)
    return df

def read_stats_csv(directory):
    df = pd.read_csv(os.path.join(directory, "stats.csv"))
    df["ts"] = pd.to_datetime(df.ts_s, unit="s")
    df["is_local"] = df.ip_src.apply(ip_is_local)
    return df

def ip_is_local(ip):
    local_prefixes = LOCAL_IP_PREFIXES
    for prefix in local_prefixes:
        if ip.startswith(prefix):
            return True
    return False

