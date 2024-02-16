import sys
import os
import json
import pandas as pd
import sqlite3

uplink = []
downlink = []

LOG_DIR = sys.argv[1]

log_files = [f'{LOG_DIR}/{file}' for file in os.listdir(LOG_DIR) if os.path.isfile(f'{LOG_DIR}/{file}') and file.endswith('txt') and ('uplink' in file or 'downlink' in file)]

for log in log_files:
    with open(log) as lf:
        log_json = json.load(lf)
        if 'uplink' in log:
            try:
                log_json = log_json['server_output_json']
            except KeyError:
                continue
        start_time = log_json['start']['timestamp']['timesecs']
        for interval in log_json['intervals']:
            interval = interval['sum']
            interval['start'] += start_time
            interval['end'] += start_time
            if 'downlink' in log:
                downlink.append(interval)
            else:
                uplink.append(interval)

uplink_df = pd.DataFrame(uplink)
uplink_conn = sqlite3.connect('uplink.db')
uplink_df.to_sql('iperf', uplink_conn)

downlink_df = pd.DataFrame(downlink)
downlink_conn = sqlite3.connect('downlink.db')
downlink_df.to_sql('iperf', downlink_conn)
