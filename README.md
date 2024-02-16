[![](https://img.shields.io/badge/WWW'24-Paper-blue)]()

# A Multifaceted Look at Starlink Performance

This is the artifacts repository of the Web Conference (WWW) 2024 paper: A Multifaceted Look at Starlink Performance

## 📖 Abstract
In recent years, Low-Earth Orbit (LEO) mega-constellations have emerged as a promising network technology and have ushered in a new era for democratizing Internet access. The Starlink network from SpaceX stands out as the only consumer-facing LEO network with over 2M+ customers and more than 4000 operational satellites. In this paper, we conduct the first-of-its-kind extensive multi-faceted analysis of Starlink network performance leveraging several measurement sources. First, based on 19.2M crowdsourced M-Lab speed test measurements from 34 countries since 2021, we analyze Starlink global performance relative to terrestrial cellular networks. Second, we examine Starlink's ability to support real-time web-based latency and bandwidth-critical applications by analyzing the performance of (i) Zoom video conferencing, and (ii) Luna cloud gaming, comparing it to 5G and terrestrial fiber. Third, we orchestrate targeted measurements from Starlink-enabled RIPE Atlas probes to shed light on the last-mile Starlink access and other factors affecting its performance globally. Finally, we conduct controlled experiments from Starlink dishes in two countries and analyze the impact of globally synchronized "15-second reconfiguration intervals" of the links that cause substantial latency and throughput variations. Our unique analysis provides revealing insights on global Starlink functionality and paints the most comprehensive picture of the LEO network's operation to date.

## 📝 Reference 
```
@inproceedings{multifacetedStarlink-www24,
	title={{A Multifaceted Look at Starlink Performance}},
  	author={Mohan, Nitinder and Ferguson, Andrew and Cech, Hendrik and Renatin, Prakita Rayyan and Bose, Rohan and Marina, Mahesh and Ott, J{\"o}rg},
	year = {2024}, 
	publisher = {Association for Computing Machinery}, 
	address = {New York, NY, USA}, 
	booktitle = {Proceedings of the Web Conference 2024},
	series = {WWW '24}
}
```

## 💾 Dataset

The data necessary for the plots needs to be downloaded before starting and is available at [mediaTUM](https://mediatum.ub.tum.de/1734703) with instructions on how to set it up. 


## 📊 Reproducibility Instructions
All plots were created with Python3.10. We recommend following our instructions to create a virtual Python environment with the package versions that we used.

```
git clone https://github.com/nitindermohan/multifaceted-starlink-performance.git
cd multifaceted-starlink-performance
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The dataset contains both raw data and processed artifacts. To only download the data required for plotting, you may use the following command.

``` sh
export DATA_PATH="$(pwd)/multifaceted-dataset"
# will follow when dataset is public
rsync ... "$DATA_PATH/"

tree -L 2 "$DATA_PATH"
/u/home/me/multifaceted-dataset/
└── data
    ├── mlab
    └── zoom
```

All plots can be created with the following commands.
``` sh
# Remember that envvar DATA_PATH needs to point to the cloned dataset (see the previous step)

# RIPE Atlas plots
jupyter nbconvert --to=html --execute ripe_atlas_figures/ripe_atlas_repr.ipynb

# MLab plots
jupyter nbconvert --to=html --execute mlab_figures/mlab_concise.ipynb

# Zoom plots
bash fig-10-zoom/plot.sh

# Cloud gaming plots
bash fig-11-gaming/plot.sh
```

