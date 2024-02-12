# RIPE Atlas Starlink Figures

With the script found in this folder, the following figures can be generated:

* Figure 3
* Figure 12
* Figure 13
* Figure 14
* Figure 15
* Figure 22

## Requirements

* Python 3.9 (tested with Python 3.9.6)
* venv

## Quick-Start

Fetch the data and set the `DATA_PATH` environment variable to the folder where the data is downloaded. The Ripe Atlas data must be in a subfolder (./atlas/ripe_Atlas_repr) of this data folder.

The execute the below commands in the terminal

```
cd /path/to/this/folder
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATA_PATH=/path/to/data/folder
jupyter nbconvert --to=html --execute ripe_atlas_repr.ipynb
```

Now, the figures are generated in the ./Figs folder and you can also see the rendered notebook in ripe_atlas_repr.html.