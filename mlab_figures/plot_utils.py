import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from descartes import PolygonPatch
from unidecode import unidecode
from matplotlib.patches import Patch
cols = plt.get_cmap("tab10").colors

def plot_cdf(df, cities, column, xlabel,
                 ax=None,
                 fig=None,
                 show=True,
                 figsize=(7, 4),
                 savefig="",
                 title="CDF",
                 city_colors={},
                 lstyles={},
                 condition=True,
                 skiplegend=False,
                 figures_path="figures", xlim=None, legendsettings={}, legendloc="lower right", xticks=None, xticklabels=None, ylabel="CDF", stripylabels=False, labelmaprule={}):
    if ax==None:
        fig, ax = plt.subplots(figsize=figsize)
    for city in cities:
        #  & (df["a_MinRTT"] < 600)
        xs = df[(df["client_Geo_City"] == city) & (condition)][column].values
        xs = sorted(xs)
        if len(xs) == 0:
            print(city)
            raise RuntimeError()
        ys = np.arange(1, len(xs) + 1) / len(xs)
        indices = []
        current = xs[0]
        for i, x in enumerate(xs): # only take max y value at each x value to smoothen out the graph
            if x != current:
                current = x
                indices.append(i - 1)
        indices.append(len(ys) - 1)
        xs = sorted(set(xs))
        ys = [ys[i] for i in indices]
        label = labelmaprule.get(city, city)
        ax.plot(xs, ys, label=label, color=city_colors[city], linestyle=lstyles[city])

    if xlim is not None:
        ax.set_xlim(*xlim)
    if xticks is not None:
        ax.set_xticks(xticks)
    if xticklabels is not None:
        ax.set_xticks(xticklabels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if stripylabels:
        ax.set_yticks(np.arange(0, 1.25, 0.25), labels=[""]*len(np.arange(0, 1.25, 0.25)))
    else:
        ax.set_yticks(np.arange(0, 1.25, 0.25))
    ax.xaxis.get_major_formatter()._usetex = False
    ax.yaxis.get_major_formatter()._usetex = False

    handles, labels = plt.gca().get_legend_handles_labels()
    sorted_hl = sorted(zip(handles, labels), key=(lambda t: t[1]), reverse=False)
    if not skiplegend:
        ax.legend([t[0] for t in sorted_hl],
                  [t[1] for t in sorted_hl], loc=legendloc, fontsize="small", ncol=2, edgecolor="k", handlelength=1, labelspacing=0.06,
                  columnspacing=0.5, handletextpad=0.3, fancybox=False)
    ax.grid(True, axis='y', linestyle='-', alpha=0.7, linewidth=0.5)
    
    ax.set_ylim((-0.05, 1.05))

    #plt.title(title)
    if fig != None:
        fig.tight_layout()
    if(savefig != ""):
        if ".pdf" in savefig:
            svg_savefig = savefig.replace(".pdf", ".svg")
            plt.savefig(os.path.join(figures_path, svg_savefig), bbox_inches="tight", pad_inches=0)
        plt.savefig(os.path.join(figures_path, savefig), bbox_inches="tight", pad_inches=0)
    if show:
        plt.show()

def plot_probe_map(city_overview_df, city_df, interesting_cities,
                       lon_bounds = (-180, 180),
                       lat_bounds = (-90, 90),
                       figsize=(7, 6),
                       annotate = True,
                       annotate_minimal = False,
                       savefig = "",
                       figures_path="figures"):
    city_colors = {city: cols[i % len(cols)] for i, city in enumerate(interesting_cities)}
    lstyles = {city: lstyle_array[i % len(lstyle_array)] for i, city in enumerate(interesting_cities)}
    
    client_country_coords_df = city_overview_df.groupby(["ClientCountry", "ClientCity"])[["lat", "lon"]].mean()
    client_country_coords_df = client_country_coords_df[(
                                    client_country_coords_df["lat"] > lat_bounds[0]) & (client_country_coords_df["lat"] < lat_bounds[1]
                                                        )]
    client_country_coords_df = client_country_coords_df[(
                                    client_country_coords_df["lon"] > lon_bounds[0]) & (client_country_coords_df["lon"] < lon_bounds[1]
                                                        )]

    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world = world[(world.name!="Antarctica")]

    def plotCountryPatch( axes, country_name, fcolor ):
        # plot a country on the provided axes
        nami = world[world.name == country_name]
        namigm = nami.__geo_interface__['features']  # geopandas's geo_interface
        namig0 = {'type': namigm[0]['geometry']['type'], \
                  'coordinates': namigm[0]['geometry']['coordinates']}
        axes.add_patch(PolygonPatch( namig0, fc=fcolor, ec="black", alpha=0.2, zorder=2, linewidth=0.0 ))


    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})

    ax.set_xlim(lon_bounds)
    ax.set_ylim(lat_bounds)

    cmap = colors.ListedColormap(cols[:-2])
    world.plot(facecolor = "grey", edgecolor="black", ax=ax, linewidth=0.2, alpha=0.2, zorder=0)

    for c in countries:
        c = "United States of America" if c == "United States" else c
        c = "Czechia" if c == "Czech Republic" else c

        if(c in world["name"].values):
            plotCountryPatch(ax, c, "#364aa088")

    client_country_df = city_overview_df.groupby(["ClientCountry", "ClientCity"])[["lat", "lon"]].mean()
    latitude, longitude = client_country_coords_df["lat"], client_country_coords_df["lon"]
    ax.scatter(longitude, latitude, 
                   sizes = [0.7],
                   color="#a8290a88",
                   zorder = 10)

    # Filtered with interesting_cities
    client_country_df = city_overview_df[city_overview_df["ClientCity"].isin(interesting_cities)].groupby(["ClientCountry", "ClientCity"])[["lat", "lon"]].mean()
    latitude, longitude = client_country_df["lat"], client_country_df["lon"]
    ax.scatter(longitude, latitude, 
                   sizes = [10.1],
                   color="green",
                   zorder = 9, marker="x")

    for x, y, label in zip(client_country_coords_df["lon"], client_country_coords_df["lat"], client_country_coords_df.index):
        if(annotate and ((not annotate_minimal) or (label[1] in interesting_cities))):
            ax.annotate(label[1], xy=(x, y), xytext=(-7, 5), textcoords="offset points")

    plt.tight_layout()
    if(savefig != ""):
        if ".pdf" in savefig:
            svg_savefig = savefig.replace(".pdf", ".svg")
            plt.savefig(os.path.join(figures_path, svg_savefig), bbox_inches="tight", pad_inches=0)
        plt.savefig(os.path.join(figures_path, savefig), bbox_inches="tight", pad_inches=0)
    plt.show()


def plot_boxplot_progression(datetime_array, data_array,
                                savefig = "",
                                figsize=(7, 6),
                                ylabel = "",
                                figures_path="figures",
                                nlegendcols=3,
                                ylim=None,
                                xlim=None,
                                decimation=1,
                                orientation="upper right"):
    """
    Plot boxplot progression. As input you give a
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    colnames = data_array[0].keys()
    colcolors = [cols[i] for i, _ in enumerate(data_array[0])]
    def adjust_box(plot):
        for i, (cn, cc) in enumerate(zip(colnames, colcolors)):
            plt.setp(plot['boxes'][i], facecolor=cc, linewidth=1)
            plt.setp(plot['medians'][i], color='yellow')
    
    width = 0.5
    xspan = len(data_array[0].keys()) + 1
    
    for i, (dt, data_dict) in enumerate(zip(datetime_array, data_array)):
        positions = np.arange(
                        i * xspan,
                        i * xspan + len(data_dict.keys())
                    )
        bp = ax.boxplot([data_dict[cn] for cn in colnames], positions=positions, 
                        widths=width, showfliers=False, patch_artist=True)
        adjust_box(bp)

    [ax.axvspan(i * xspan - 1, i * xspan + xspan - 1, facecolor="k", alpha=0.2)
        for i in range(len(datetime_array))
        if i % 2 == 1]

    ax.set_xticks(np.arange(
                        int(xspan / 2),
                        1 + xspan * len(datetime_array),
                        xspan
                    ))
    ax.set_xticklabels([dt.strftime("%Y/%m") for dt in datetime_array])
    ax.xaxis.set_tick_params(rotation=15)
    ax.set_ylabel(ylabel)

    if xlim != None:
        if xlim[1] < 0:
            xlim_ = [xlim[0] * xspan - 1, (len(datetime_array) - 1) * xspan + xspan - 1]
        else:
            xlim_ = [xlim[0] * xspan - 1, (xlim[1] + xlim[0]-1) * xspan + xspan - 1]
        ax.set_xlim(xlim_)
    else:
        ax.set_xlim([-1, (len(datetime_array) - 1) * xspan + xspan - 1])
    if ylim != None:
        ax.set_ylim(ylim)
    #ax.set_yticks(np.arange(0, 700, 100))

    ax.xaxis.get_major_formatter()._usetex = False
    ax.yaxis.get_major_formatter()._usetex = False

    #handles = [Patch(facecolor=continent_colors[target1]), Patch(facecolor=continent_colors[target2]),
    #           Patch(facecolor=continent_colors[cont])]
    handles = [Patch(facecolor=cols[i]) for i, _ in enumerate(data_array[0])]
    labels = colnames
    
    #[label.set_visible(False) for label in ax.xaxis.get_ticklabels()]
    #for label in ax.xaxis.get_ticklabels()[::decimation]:
    #    label.set_visible(True)

    ax.legend(handles, labels, handlelength=1, labelspacing=0.06, columnspacing=0.5, handletextpad=0.3,
              loc=orientation, fancybox=False, edgecolor="k", fontsize="small", ncol=nlegendcols)
    plt.grid(True, axis='y', linestyle='--')

    fig.tight_layout()
    if(savefig != ""):
        if ".pdf" in savefig:
            svg_savefig = savefig.replace(".pdf", ".svg")
            plt.savefig(os.path.join(figures_path, svg_savefig), bbox_inches="tight", pad_inches=0)
        plt.savefig(os.path.join(figures_path, savefig), bbox_inches="tight", pad_inches=0)
    plt.show()
