#!/usr/bin/python3

import sys
import json
import matplotlib.pyplot as plt
import sqlite3
import pandas

# Setting global font to "CMU Sans Serif"
from matplotlib import rcParams
rcParams["font.family"] = "CMU Sans Serif"
rcParams['svg.fonttype'] = 'none'
rcParams.update({"font.size": 10})
# This will compile plots to be Latex compatible
#plt.rc('text', usetex=True)

OPTIMISATION_START=0

DOWNLINK_START_TIME = 1684148817 # 15 May 2023 11:06:57
DOWNLINK_END_TIME = DOWNLINK_START_TIME+195 # 15 May 2023 11:10:12

UPLINK_START_TIME = 1684148397 # 15 May 2023 10:59:57
UPLINK_END_TIME = UPLINK_START_TIME+195 # 15 May 2023 11:03:12

# It is necessary to shift the dataset because the raw timestamps are incorrect.
# This is due to two errors:
# 1. NTP not being active on the client, resulting in incorrect downlink timestamps
# 2. Iperf rounding down the initial timestamp to the nearest second
# For more information (and the discussion with reviewers), see the publicly-available reviewer comments
DOWNLINK_OFFSET = 1.25
UPLINK_OFFSET = 0.25


conn = sqlite3.connect('downlink.db')
downlink_df = pandas.read_sql(f'SELECT * FROM iperf WHERE start >= {DOWNLINK_START_TIME} and end <= {DOWNLINK_END_TIME}', conn)
conn.close()

conn = sqlite3.connect('uplink.db')
uplink_df = pandas.read_sql(f'SELECT * FROM iperf WHERE start >= {UPLINK_START_TIME} and start <= {UPLINK_END_TIME}', conn)
conn.close()

fig, axs = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [1,1]}, figsize=(2.8, 2.4))

axs[0].plot(downlink_df['start']-DOWNLINK_START_TIME + DOWNLINK_OFFSET, downlink_df['bits_per_second'] / (1024*1024), label='Downlink')
axs[1].plot(uplink_df['start']-UPLINK_START_TIME + UPLINK_OFFSET, uplink_df['bits_per_second'] / (1024*1024), label='Uplink')

optimisation_interval = 0
y_max=340
while optimisation_interval < 300:
    for ax in axs:
        ax.plot([optimisation_interval, optimisation_interval], [0, y_max], color='#2d000ef4', linestyle='--', label='Reconfiguration Interval' if optimisation_interval == 0 else None)
    optimisation_interval += 15

axs[0].set_xlim(0,195)
axs[0].set_ylim(0, y_max)

axs[1].set_xlim(0,195)
axs[1].set_ylim(0, 80)

axs[1].set_xlabel("Experiment time [s]")
axs[1].set_xticks(range(0,195,30))
fig.text(0,0.5, "Throughput [Mbps]", ha="center", va="center", rotation=90)

fig.tight_layout()
plt.savefig("throughput.svg", bbox_inches="tight", pad_inches=0)
