#!/usr/bin/env python3

import fileinput
import re
import json

wall_pattern = re.compile(r"\[\[\"wall\"\]\,(\d+)\]\n")
receive_pattern = re.compile(r"\[\[\"receive\"\]\,(\d+)\]\n")
rtt_pattern = re.compile(r"\[\[\"rtt\"\]\,(\d+)\]\n")
send_pattern = re.compile(r"\[\[\"send\"\]\,(\d+)\]\n")

current_dict = None
for line in fileinput.input():
    if match := re.fullmatch(wall_pattern, line):
        current_dict = {'epoch': int(match[1])}
    elif match := re.fullmatch(receive_pattern, line):
        current_dict['receive'] = int(match[1])
    elif match := re.fullmatch(rtt_pattern, line):
        current_dict['rtt'] = int(match[1])
    elif match := re.fullmatch(send_pattern, line):
        current_dict['send'] = int(match[1])
        try:
            print(f'{current_dict["epoch"]},{current_dict["send"]},{current_dict["receive"]},{current_dict["rtt"]}')
        except (BrokenPipeError, IOError):
            pass
        current_dict = None
