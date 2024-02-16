#!/bin/bash
if [[ $# -ne 1 ]]
then
  echo "Usage: ./save_data.sh <IRTT zst filepath>"
  exit 1
fi

if [ -f irtt.db ]; then
  echo 'Database already exists, data will be added...'
else
  echo 'Database does not exist, and will be created'
  sqlite3 irtt.db '.read schema.sql'
fi

unzstd -c $1 | jq -c --stream 'select(.[1] and ((.[0][2] == "timestamps" and .[0][3] == "client" and .[0][4] == "send" and .[0][5] == "wall") or (.[0][2] == "delay"))) | del(.[0][0:-1])' | ./parse_irtt_json.py | sqlite3 -csv ./irtt.db ".separator ','" ".import '|cat -' irtt"