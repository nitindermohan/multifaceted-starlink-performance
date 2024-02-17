#!/usr/bin/env python3

import matplotlib.pyplot as plt
import sys
import sqlite3
import pandas

# unix epoch for the starting time for the duration
START_TIME=1681733787 # 17 April 2023 12:16:27

# unix epoch for the ending time for the duration
END_TIME = START_TIME + 195

# do we show a raw plot or a reduced plot
REDUCED=False

# the first interval between optimisation intervals in the plot
OPTIMISATION_START=0



def read_in_values(irtt_db_file, start_epoch_seconds, start_end_seconds):
    """
    Retreive the IRTT round-trip time data for the given duration from the database.

    :param irtt_db_file: the SQLite3 database file to read from
    :param start_epoch_seconds: the start time (unix epoch) of the time period
    :param start_end_seconds: the end time time (unix epoch) of the time period
    :return: a pandas dataframe containing the round-trip-time data
    """
    conn = sqlite3.connect(irtt_db_file)
    start_time = start_epoch_seconds * 1e9
    end_time = start_end_seconds * 1e9
    df = pandas.read_sql(f'SELECT epoch,rtt FROM irtt WHERE epoch >= {start_time} AND epoch <= {end_time}', conn)
    return df



def reduce_df(df):
    """
    Reduce the data by averaging it over one second intervals

    :param df: the pandas dataframe containing the data to reduce
    :return: a pandas dataframe containing the reduced data
    """
    buckets = range(int((START_TIME-1)*1e9), int((END_TIME+1)*1e9), int(1e9))
    df['epoch category'] = pandas.cut(df['epoch'], buckets)
    df['reduced_rtt'] = df.groupby('epoch category')['rtt'].transform('mean')
    df = df.drop_duplicates(subset=['epoch category', 'reduced_rtt'])
    df = df[['epoch', 'reduced_rtt']]
    df = df.reset_index(drop=True)
    df = df.rename(columns={'reduced_rtt': 'rtt'})
    return df



def plot_data(dish_a, dish_b):
    """
    Draw the plot showing the IRTT values for two dishes

    :param dish_a: a pandas dataframe containing IRTT data to plot for dish A
    :param dish_b: a pandas dataframe containing IRTT data to plot for dish B
    :return: nothing
    """

    # Plot the raw IRTT measurements
    fig, axs = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [1,1]}, figsize=(2.8, 2.4))
    axs[0].scatter(dish_a['epoch'], dish_a['rtt'] / 1e6, s=0.5, rasterized=True)
    axs[1].scatter(dish_b['epoch'], dish_b['rtt'] / 1e6, s=0.5, rasterized=True)

    # Plot the reduced IRTT measurements (averaged over one second)
    dish_a = reduce_df(dish_a)
    dish_b = reduce_df(dish_b)
    axs[0].plot(dish_a['epoch'], dish_a['rtt'] / 1e6, color='red')
    axs[1].plot(dish_b['epoch'], dish_b['rtt'] / 1e6, color='red')

    main_axs = axs[1]

    # limit the x axis to only the IRTT data
    y_max = 100
    for ax in axs:
        ax.set(xlim=(dish_a['epoch'][0], dish_a['epoch'][dish_a['epoch'].size-1]), ylim=(0, y_max))

    # fix the x axis so the ticks and labels are in seconds
    num_seconds = round((dish_a['epoch'][dish_a['epoch'].size-1] - dish_a['epoch'][0]) / 1e9)
    secs_step = 30
    plt.xticks(list(range(dish_a['epoch'][0], dish_a['epoch'][0]+int(num_seconds*1e9), int(secs_step*1e9))), list(range(0, num_seconds, secs_step)))

    # add the labels
    main_axs.set_xlabel("Experiment time [s]")
    fig.text(0,0.5, "Dish 1 and 2 RTT [ms]", ha="center", va="center", rotation=90)

    # add the optimisation intervals
    optimisation_interval = OPTIMISATION_START
    while optimisation_interval < num_seconds:
        adjusted_x = dish_a['epoch'][0] + (optimisation_interval*1e9)
        for ax in axs:
            ax.plot([adjusted_x, adjusted_x], [0, y_max], color='#2d000ef4', linestyle='--')
        optimisation_interval += 15

    # show the plot
    plt.savefig("rtt.pdf", bbox_inches="tight", pad_inches=0, dpi=600)
    plt.savefig("rtt.svg", bbox_inches="tight", pad_inches=0, dpi=600)


if __name__ == '__main__':
    # get the IRTT data from the database
    dish_a = read_in_values('dish-1.db', START_TIME, END_TIME)
    dish_b = read_in_values('dish-2.db', START_TIME, END_TIME)
    plot_data(dish_a, dish_b)
