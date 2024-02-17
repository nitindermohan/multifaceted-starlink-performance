#!/bin/bash

cd "$(dirname -- "$0")"

# Check for required installed programmes
if ! which unzstd; then
  echo 'unzstd command not found on $PATH. Aborting'
  exit 1
fi
if ! which jq; then
  echo 'jq command not found on $PATH. Aborting'
  exit 1
fi
if ! which sqlite3; then
  echo 'sqlite3 command not found on $PATH. Aborting'
  exit 1
fi

# Convert the relevent data from dish 1 from raw IRTT logs to an SQLite DB
./create_sqlite_db.sh $DATA_PATH/controlled/irtt/dish-1/230417T120001_irtt.json.zst
mv irtt.db dish-1.db

# Convert the relevent data from dish 2 from raw IRTT logs to an SQLite DB
./create_sqlite_db.sh $DATA_PATH/controlled/irtt/dish-2/irtt.zst
mv irtt.db dish-2.db

# Create the plot
python ./plot.py
