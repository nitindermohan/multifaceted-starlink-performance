import matplotlib.pyplot as plt
import sys
import os
import pandas
import json
import datetime
import sqlite3
import numpy

# do we show a raw plot or a reduced plot
REDUCED=False

# the first interval between optimisation intervals in the plot
OPTIMISATION_START=13

fig, axs = plt.subplots(2, sharex=False, figsize=(2.8, 2.4)) #down from 2.2


######################
# Load the IRTT Data #
######################

times = []
rtts = []
with open(f'{sys.argv[1]}/controlled/irtt_fov/2023-10-08_18-41-11.json') as f:
    jj = json.load(f)
for rt in jj['round_trips']:
    if rt['delay'] == {}: continue
    times.append(rt['timestamps']['client']['send']['wall'] / 1e9)
    rtts.append(rt['delay']['rtt'])
irtt = pandas.DataFrame({'epoch': times, 'rtt': rtts})

######################
# Plot the IRTT data #
######################

axs[0].scatter(irtt['epoch'] - min(irtt['epoch']), irtt['rtt'] / 1e6, s=0.5, rasterized=True)

x_size = max(irtt['epoch']) - min(irtt['epoch'])
y_max = 100 #max(irtt['rtt'] / 1e6)
axs[0].set(xlim=(0, x_size), ylim=(10, y_max))

axs[0].set_xlabel("Experiment Duration [s]")
axs[0].set_ylabel("RTT [ms]")
axs[0].set_yticks([10,55,100])

first_time_ds = datetime.datetime.fromtimestamp(min(irtt['epoch']))
first_interval_ds = datetime.datetime(first_time_ds.year, first_time_ds.month, first_time_ds.day, first_time_ds.hour, first_time_ds.minute-1, 57)
first_interval = first_interval_ds.timestamp()
while first_interval <= max(irtt['epoch']) + 15:
    axs[0].plot([first_interval - min(irtt['epoch']), first_interval - min(irtt['epoch'])   ], [0, y_max], color='#2d000ef4', linestyle='--', label='Reconfiguration Interval' if first_interval == min(irtt['epoch']) else None)
    first_interval += 15

######################
# Plot the GRPC data #
######################

def get_intervals(time_list):
    intervals = []
    time_list = sorted(time_list)
    current_interval = (time_list[0], time_list[0])
    for ts in time_list[1:]:
        if ts == current_interval[1] + 1:
            current_interval = (current_interval[0], ts)
        elif ts > current_interval[1] + 1:
            intervals.append(current_interval)
            current_interval = (ts,ts)
        elif ts < current_interval[1] + 1:
            raise Exception("Somehow gone backwards in time in a sorted list")
    # don't forget to append the last interval!
    intervals.append(current_interval)
    return intervals

def get_connected_intervals(grpc_df):
    connected_ts = sorted(grpc_df[grpc_df['state'] == 'CONNECTED']['time'].tolist())
    return get_intervals(connected_ts)

def get_prev_interval(ts):
    dts = datetime.datetime.fromtimestamp(ts)
    if dts.second >= 12 and dts.second < 27:
        prev_i = datetime.datetime(year=dts.year, month=dts.month, day=dts.day, hour=dts.hour, minute=dts.minute, second=12)
    elif dts.second >= 27 and dts.second < 42:
        prev_i = datetime.datetime(year=dts.year, month=dts.month, day=dts.day, hour=dts.hour, minute=dts.minute, second=27)
    elif dts.second >= 42 and dts.second < 57:
        prev_i = datetime.datetime(year=dts.year, month=dts.month, day=dts.day, hour=dts.hour, minute=dts.minute, second=42)
    elif dts.second >= 57:
        prev_i = datetime.datetime(year=dts.year, month=dts.month, day=dts.day, hour=dts.hour, minute=dts.minute, second=57)
    else:
        prev_i = datetime.datetime(year=dts.year, month=dts.month, day=dts.day, hour=dts.hour, minute=dts.minute, second=57)
        prev_i -= datetime.timedelta(minutes=1)
    return int(prev_i.timestamp())

grpc_connection_intervals = []

grpc_path = f'{sys.argv[1]}/controlled/grpc_fov'
grpc_files = [f'{grpc_path}/{file}' for file in os.listdir(grpc_path) if os.path.isfile(f'{grpc_path}/{file}') and file.endswith('.db')]
for grpc_file in grpc_files:
    conn = sqlite3.connect(grpc_file)
    grpc_df = pandas.read_sql(f'SELECT * FROM status', conn)
    conn.close()
    grpc_connection_intervals += get_connected_intervals(grpc_df)


start_seconds_to_prev_interval = [abs(get_prev_interval(iv[0])-iv[0]) for iv in grpc_connection_intervals]
end_seconds_to_prev_interval = [abs(get_prev_interval(iv[1])-iv[1]) for iv in grpc_connection_intervals]

num_intervals = len(grpc_connection_intervals)
barchart_start = [len([val for val in start_seconds_to_prev_interval if val==i]) / num_intervals for i in range(15)]
barchart_end = [len([val for val in end_seconds_to_prev_interval if val==i]) / num_intervals for i in range(15)]

rects = axs[1].bar(numpy.arange(15) - 0.2, barchart_start, width=0.4, label='Connectivity Start')
rects = axs[1].bar(numpy.arange(15) + 0.2, barchart_end, width=0.4, label='Connectivity End')

axs[1].set_xlabel(f'Seconds to prev. R.I.')
axs[1].set_ylabel('Probability')
axs[1].set_xticks(range(0,15,2))
axs[1].set_yticks([0, 0.2, 0.4])

# show the plot
plt.legend(fontsize=8, frameon=False)
plt.savefig("fov.svg", bbox_inches="tight", pad_inches=0, dpi=600)
