"""Example visualization of data.

TODO: size of mean groups & annotations for mean group size
TODO: separate mean and individual data
TODO: calculate mean from individual data
TODO: fitting of histogram (lognormal)
"""
from pathlib import Path
from typing import Iterable, Optional

# ------------------------------------------------------------------------------
# plt.style.use('science')
import matplotlib
import matplotlib.axes
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from protein_distribution.console import console
from protein_distribution.protein_info import get_protein_categories, get_proteins
from protein_distribution.significance_testing import (
    process_stratification_data,
    stratification_info,
)


SMALL_SIZE = 12
MEDIUM_SIZE = 15
BIGGER_SIZE = 25

matplotlib.rc("font", size=SMALL_SIZE)  # controls default text sizes
matplotlib.rc("axes", titlesize=SMALL_SIZE)  # fontsize of the axes title
matplotlib.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
matplotlib.rc("xtick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
matplotlib.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
matplotlib.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize
matplotlib.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title
# ------------------------------------------------------------------------------


# handle colors
cmap = matplotlib.cm.get_cmap("tab20")
studies = [
    "Achour2014",
    "Achour2017",
    "Asai1996",
    "Couto2019",
    "Fallon2016",
    "Gao2016",
    "Groer2014",
    "Inoue2000",
    "Kawakami2011",
    "Karlgren2012",
    "Kawakami2011",
    "Kimoto2012",
    "Li2015",
    "Michaels2014",
    "Ohtsuki2012",
    "Olesen2000",
    "Prasad2014",
    "Seibert2009",
    "Snawder2000",
    "Takahashi2021",
    "Tucker2012",
    "Vasilogianni2022",
    "Vildhede2015",
    "Wang2015",
    "Wegler2022",
]
study2color = {study: cmap(k / 20) for k, study in enumerate(studies)}


def plot_protein_abundance(
    data: pd.DataFrame, protein_id: str, image_dir: Optional[Path]
) -> Figure:
    """Plot data for a single enzyme for multiple studies."""

    # subset of abundance for protein
    df_protein = data[data.protein == protein_id]
    sids = list(reversed(sorted(df_protein.sid.unique())))

    # figsize=(10, 0.4 * len(sids))
    height = max(0.4 * len(sids), 3)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, height), dpi=300)
    fig.subplots_adjust(left=0.3, bottom=0.2)
    labels = []
    for k, sid in enumerate(sids):
        study = sid.split("_")[0]
        color = study2color[study]
        df_sid = df_protein[df_protein.sid == sid]
        y = k * np.ones(shape=(len(df_sid)))

        values = df_sid["value"].values
        means = df_sid["mean"].values
        sds = df_sid["sd"].values

        # plot individual data
        kwargs = {
            "linestyle": "None",
            "markeredgecolor": "black",
            "markersize": 9,
            "color": color,
        }

        if not np.all(np.isnan(values)):
            ax.plot(values, y, marker="o", alpha=0.7, **kwargs)
            # annotate points
            # for i in range(len(y)):
            #    ax.annotate(sid, (x[i], y_values[i]))

        # plot mean data
        # FIXME: add SD (calculate SD in dataset)
        # FIXME: add [min-max] if available
        if not np.all(np.isnan(means)):
            # ax.plot(means, y, marker="s", alpha=1.0, **kwargs)
            ax.errorbar(
                x=means, y=y, xerr=sds, marker="s", alpha=0.8, ecolor="black", **kwargs
            )
            # for i in range(len(x)):
            #     ax.annotate(sid, (x[i], y_means[i]))
        n_values = np.count_nonzero(~np.isnan(values))
        n_means = np.count_nonzero(~np.isnan(means))
        labels.append(
            f"{sid}\nn={n_means if n_means else ' '}|{n_values if n_values else ' '}"
        )

    # ax.set_xlim(left=0)
    ax.set_xlabel("Protein abundance [pmol/mg]", fontdict={"weight": "bold"})
    # ax.set_ylabel("Dataset", fontdict={"weight": "bold"})
    ax.set_title(protein_id, fontdict={"weight": "bold", "size": 20})
    # ax.legend(loc=(1.04, 0))
    ax.set_yticks(
        ticks=range(len(labels)),
        labels=labels,
        weight="bold",
        size=8,
    )

    # plt.show()
    if image_dir:
        fig.savefig(image_dir / f"{protein_id}.svg")
        fig.savefig(image_dir / f"{protein_id}.png", bbox_inches="tight")
    return fig


def plot_protein_histogram(
    data: pd.DataFrame, protein_id: str, image_dir: Optional[Path]
) -> Optional[Figure]:
    """Plot histogram."""

    # subset of abundance for individual protein
    df_protein = data[(data.protein == protein_id) & (~pd.isnull(data.value))]
    studies = list(sorted(df_protein.study.unique()))
    console.print(studies)

    # get all values
    values_list = []
    labels = []
    colors = []
    # FIXME: only use individual values
    for _, study in enumerate(studies):
        # study = sid.split("_")[0]
        colors.append(study2color[study])
        df_sid = df_protein[df_protein.study == study]

        values = df_sid["value"].values
        print(study, values)
        values_list.append(values)
        labels.append(study)

    if not values_list:
        console.log(f"No data for '{protein_id}', no plot generated.")
        return None

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 7), dpi=300)
    # fig.subplots_adjust(left=0.2, bottom=0.2)

    ax.hist(
        values_list,
        bins=20,
        stacked=True,
        density=True,
        color=colors,
        edgecolor="black",
        label=labels,
    )

    ax.set_xlabel("Protein abundance [pmol/mg]", fontdict={"weight": "bold"})
    ax.set_ylabel("Density", fontdict={"weight": "bold"})
    ax.set_title(protein_id, fontdict={"weight": "bold", "size": 20})
    ax.legend()
    if image_dir:
        fig.savefig(image_dir / f"{protein_id}_hist.svg")
        fig.savefig(image_dir / f"{protein_id}_hist.png", bbox_inches="tight")
    return fig


def plot_correlation(
    data: pd.DataFrame, pid1: str, pid2: str, image_dir: Optional[Path]
) -> Figure:
    """Plot correlation."""

    df = data[["study", "individual", "tissue", pid1, pid2]]
    # only individual data
    row_index = ~pd.isnull(df[pid1]) & ~pd.isnull(df[pid2])
    df = df[row_index]

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5), dpi=300)
    fig.subplots_adjust(left=0.2, bottom=0.2)
    for study in df.study.unique():
        df_subset = df[df.study == study]
        ax.plot(
            df_subset[pid1],
            df_subset[pid2],
            "o",
            markeredgecolor="black",
            label=study,
            alpha=0.8,
            markersize=10,
        )
    ax.set_xlabel(f"{pid1} [pmol/mg]", fontdict={"weight": "bold"})
    ax.set_ylabel(f"{pid2} [pmol/mg]", fontdict={"weight": "bold"})
    ax.legend(prop={"size": 8})
    plt.show()
    if image_dir:
        fig.savefig(image_dir / f"correlation_{pid1}_{pid2}.svg")
        fig.savefig(image_dir / f"correlation_{pid1}_{pid2}.png", bbox_inches="tight")


def plot_multi_stratified(
    data: pd.DataFrame,
    category: str,
    image_dir: Optional[Path],
    stratification_key: str = "sex",
) -> Figure:
    """Plot multiple proteins stratified by information.

    existing groups and filtered groups:

    sex: [M, F, NR] -> [M, F]
    smoking [Y, N, NR] -> [Y, N]
    alcohol [Y, N, NR] -> [Y, N]
    ethnicity [caucasian, hispanic, african american, NR] -> [caucasian, african american, hispanic]
    age_group [adolescent, young, middle aged, elderly, NR] -> [middle aged, elderly]
    bmi_group [underweight, normal weight, overweight, obese, NR] -> [normal weight, overweight, obese]
    """

    # process stratification data
    df_protein = process_stratification_data(
        data=data, stratification_key=stratification_key
    )

    # order by mean
    means = {}
    for p in df_protein.protein.unique():
        means[p] = df_protein[df_protein.protein == p].value.mean()
    keys = list(means.keys())
    values = list(means.values())
    sorted_value_index = np.argsort(values)
    proteins_sorted = list(reversed([keys[i] for i in sorted_value_index]))

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 10), dpi=300)
    fig.subplots_adjust(left=0.2, bottom=0.2)

    # creating boxplot
    groups = stratification_info[stratification_key]["groups"]
    colors = stratification_info[stratification_key]["colors"]
    sns.boxplot(
        ax=ax,
        y="value",
        x="protein",
        hue=stratification_key,
        hue_order=groups,
        data=df_protein,
        order=proteins_sorted,
        palette=colors,
    )

    # adding data points
    sns.stripplot(
        ax=ax,
        y="value",
        x="protein",
        hue=stratification_key,
        hue_order=groups,
        dodge=True,
        data=df_protein,
        order=proteins_sorted,
        color="black",
        edgecolor="black",
        size=5,
        alpha=0.5,
    )

    ax.set_xlabel("Protein abundance [pmol/mg]", fontdict={"weight": "bold"})
    ax.set_ylabel("Protein", fontdict={"weight": "bold"})

    n_proteins = len(df_protein.protein.unique())
    title = f"{category} | {stratification_key} (m={n_proteins})"
    ax.set_title(title, fontdict={"weight": "bold", "size": 20})
    ax.set_yscale("log")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, horizontalalignment="center")
    plt.show()

    if image_dir:
        fig.savefig(image_dir / f"{category}_boxplot_{stratification_key}.svg")
        fig.savefig(
            image_dir / f"{category}_boxplot_{stratification_key}.png",
            bbox_inches="tight",
        )

    return fig


def plot_multi(
    data: pd.DataFrame,
    title: str,
    image_dir: Optional[Path],
) -> Figure:
    """Plot multiple proteins as boxplot."""

    # subset of abundance for individual protein
    df_protein = data[~pd.isnull(data.value)]

    # order by mean
    means = {}
    for p in df_protein.protein.unique():
        means[p] = df_protein[df_protein.protein == p].value.mean()
    keys = list(means.keys())
    values = list(means.values())
    sorted_value_index = np.argsort(values)
    proteins_sorted = list(reversed([keys[i] for i in sorted_value_index]))

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 20), dpi=300)
    fig.subplots_adjust(left=0.2, bottom=0.2)

    # creating boxplot
    sns.boxplot(ax=ax, x="value", y="protein", data=df_protein, order=proteins_sorted)

    # adding data points
    sns.stripplot(
        ax=ax,
        x="value",
        y="protein",
        data=df_protein,
        order=proteins_sorted,
        # jitter=2.0,
        color="black",
        edgecolor="black",
        size=5,
        alpha=0.5,
    )

    ax.set_xlabel("Protein abundance [pmol/mg]", fontdict={"weight": "bold"})
    ax.set_ylabel("Protein", fontdict={"weight": "bold"})
    ax.set_title(title, fontdict={"weight": "bold", "size": 20})
    ax.set_xscale("log")
    plt.show()

    category = title.split(" ")[0]
    if image_dir:
        fig.savefig(image_dir / f"{category}_boxplot.svg")
        fig.savefig(image_dir / f"{category}_boxplot.png", bbox_inches="tight")

    return fig


def run_all_visualization() -> None:
    """Run all visualizations."""
    # Load data
    from protein_distribution import DATA_MERGED_XLSX, DATA_XLSX, RESULTS_DIR

    df_abundance = pd.read_excel(DATA_XLSX, sheet_name="Abundance")
    del df_abundance["comments"]
    df_abundance["sid"] = df_abundance["study"] + "_" + df_abundance["source"]

    # data_group = pd.read_excel(DATA_MERGED_XLSX, sheet_name="group_data")
    # data_individual = pd.read_excel(DATA_MERGED_XLSX, sheet_name="group_data")

    proteins = get_proteins(df_abundance, uniprot=True)
    protein_categories = get_protein_categories(proteins)

    # Create plots
    # for protein_id in ["CYP1A2", "CYP2D6", "CYP2E1"]:
    image_dir = RESULTS_DIR / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    # plot_protein_abundance(
    #     data=df_abundance,
    #     protein_id="CYP2E1",
    #     image_dir=image_dir,
    # )
    # plot_protein_histogram(
    #     data=df_abundance,
    #     protein_id="CYP2E1",
    #     image_dir=image_dir,
    # )

    # two protein correlation plots
    if True:
        # with merged data
        correlation_individuals: pd.DataFrame = pd.read_excel(
            DATA_MERGED_XLSX, sheet_name="individual_correlation"
        )
        for pids in [
            # example cyps
            ["CYP2C8", "CYP1A2"],  # positive
            ["CYP4A11", "CYP2C8"],  # positive
            ["CYP3A4", "CYP2B6"],  # positive
            ["CYP2A7", "CYP27A1"],  # negative
            ["CYP2U1", "CYP2D6"],  # negative
            # example ugts
            ["UGT2B15", "UGT1A9"],  # positive
            ["UGT2B7", "UGT2B4"],  # positive
            ["UGT1A9", "UGT1A1"],  # positive
            ["UGT2A3", "UGT1A4"],  # negative
            # example abcs
            ["ABCA8", "ABCB11"],
            ["ABCB7", "ABCE1"],
            # example slcs
            ["SLC27A4", "SLCO1B3"],
        ]:
            plot_correlation(
                data=correlation_individuals,
                pid1=pids[0],
                pid2=pids[1],
                image_dir=image_dir,
            )

    if True:
        # overview plots of categories
        # FIXME: update with merged data
        df_individual_data = pd.read_excel(
            DATA_MERGED_XLSX, sheet_name="individual_data"
        )
        for category in protein_categories.keys():
            # filter by category
            df_category = df_individual_data[
                df_individual_data.protein.isin(protein_categories[category])
            ]
            plot_multi(
                df_category,
                title=f"{category} (m={len(protein_categories[category])})",
                image_dir=image_dir,
            )
            plt.show()

    if True:
        df_individual_data = pd.read_excel(
            DATA_MERGED_XLSX, sheet_name="individual_data"
        )
        for category in ["cyp", "ugt", "slc", "abc"]:
            df_category = df_individual_data[
                df_individual_data.protein.isin(protein_categories[category])
            ]

            for stratification_key in [
                "sex",
                "smoking",
                "alcohol",
                "ethnicity",
                "age_group",
                "bmi_group",
            ]:
                plot_multi_stratified(
                    df_category,
                    stratification_key=stratification_key,
                    category=category,
                    image_dir=image_dir,
                )
                plt.show()

    if True:
        # FIXME: without merged data
        # individual plots
        for category, proteins in protein_categories.items():
            category_dir = image_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)

            for protein_id in proteins:
                console.rule(protein_id, align="left", style="white")

                plot_protein_abundance(
                    data=df_abundance,
                    protein_id=protein_id,
                    image_dir=category_dir,
                )
                plot_protein_histogram(
                    data=df_abundance,
                    protein_id=protein_id,
                    image_dir=category_dir,
                )


if __name__ == "__main__":
    run_all_visualization()
