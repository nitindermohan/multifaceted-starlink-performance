# M-Lab Speedtest Starlink Figures

With the script found in this folder, the following figures can be generated:

* Figure 6
* Figure 7
* Figure 8
* Figure 9
* Figure 19
* Figure 20
* Figure 21

## Requirements

* Python 3.10 (tested with Python 3.10.12)
* venv

## Quick-Start

Before running the script, make sure you fetch the data and set the `DATA_PATH` variable in the following accordingly.

```
cd /path/to/this/folder
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DATA_PATH=/path/to/the/fetched/data jupyter nbconvert --to=html --execute mlab_concise.ipynb
```

Now, the figures are generated in the `./figures` folder and you can also see the rendered notebook in `mlab_concise.html`.
