"""Create tables with correlation information.

Correlation coefficient, p-value, significance.
sig.level = c(0.001, 0.01, 0.05),
"""

from typing import Dict

# ------------------------------------------------------------------------------
import matplotlib
import matplotlib.axes
import matplotlib.pyplot
import pandas as pd
from matplotlib import pyplot as plt

from protein_distribution import RESULTS_DIR
from protein_distribution.console import console


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


def correlation_volcano_plot(
    category: str, cutoff_pvalue: float = 0.05, cutoff_correlation: float = 0.5
) -> None:
    """Volcano plot of the correlation coeffient."""

    # load correlations and p-values
    df_M = pd.read_table(
        RESULTS_DIR / "correlation" / f"M_individual_correlation_{category}.csv",
        sep=",",
    )
    df_M.set_index(keys="Unnamed: 0", inplace=True)

    df_p = pd.read_table(
        RESULTS_DIR / "correlation" / f"p_individual_correlation_{category}.csv",
        sep=",",
    )
    df_p.set_index(keys="Unnamed: 0", inplace=True)
    console.rule(align="left", title=category)

    columns = df_M.columns

    # plot all data points
    labels = []
    correlations = []
    pvalues = []
    for kx, protein_x in enumerate(columns):
        for ky, protein_y in enumerate(columns):
            if kx >= ky:
                continue
            if category in {"cyp", "ugt"}:
                label = f"{protein_x[3:]}-{protein_y[3:]}"
            else:
                label = f"{protein_x}~{protein_y}"
            correlation = df_M.iloc[kx, ky]
            pvalue = df_p.iloc[kx, ky]

            labels.append(label)
            correlations.append(correlation)
            pvalues.append(pvalue)

    df_data = pd.DataFrame(
        {"label": labels, "correlation": correlations, "pvalue": pvalues}
    )
    df_data.sort_values(by=["correlation"])
    console.print(df_data)

    # create plot
    ax: matplotlib.axes.Axes
    fig, ax = plt.subplots(nrows=1, ncols=1, dpi=300, figsize=(10, 8))
    ax.set_xlabel("Correlation", fontweight="bold")
    ax.set_ylabel("p-value", fontweight="bold")
    if category == "cyp":
        title = "Cytochrome P450 (CYP)"
    elif category == "ugt":
        title = "UDP-glucuronosyltransferase (UGT)"
    else:
        title = category
    # fig.suptitle(title)
    ax.set_title(title, fontweight="bold", fontsize=16)

    # lines
    line_kwargs = {"linewidth": 1.0, "linestyle": "-", "color": "black"}
    ax.axhline(y=cutoff_pvalue, **line_kwargs)
    ax.axvline(x=-cutoff_correlation, **line_kwargs)
    ax.axvline(x=+cutoff_correlation, **line_kwargs)

    # points with text annotations
    for k, label in enumerate(labels):
        pvalue = pvalues[k]
        correlation = correlations[k]

        kwargs = {
            "color": "darkgrey",
            "alpha": 0.5,
        }
        if correlation > cutoff_correlation and pvalue < cutoff_pvalue:
            kwargs = {
                "color": "tab:blue",
                "alpha": 0.9,
            }
        elif correlation < -cutoff_correlation and pvalue < cutoff_pvalue:
            kwargs = {
                "color": "tab:red",
                "alpha": 0.9,
            }

        ax.plot(
            correlation,
            pvalue,
            # linestyle="",
            marker="o",
            markersize=7,
            linestyle="",
            # markeredgecolor="black",
            **kwargs,
        )

        if abs(correlation) > cutoff_correlation and pvalue < cutoff_pvalue:
            ax.annotate(
                text=label,
                xy=(correlation, pvalue),
                fontsize="xx-small",
                fontweight="bold",
                # backgroundcolor="white",
                rotation=0,
            )
    ax.set_yscale("log")
    ax.grid(True)
    ylim = ax.get_ylim()
    ax.set_ylim(ylim[1], ylim[0])

    fig.savefig(
        RESULTS_DIR / "correlation" / f"volcano_{category}.png", bbox_inches="tight"
    )
    fig.savefig(RESULTS_DIR / "correlation" / f"volcano_{category}.svg")

    plt.show()


def correlation_tables() -> None:
    """Create correlation tables."""
    dfs_correlation: Dict[str, pd.DataFrame] = {}
    for category in categories:
        df_M = pd.read_table(
            RESULTS_DIR / "correlation" / f"M_individual_correlation_{category}.csv",
            sep=",",
        )
        df_p = pd.read_table(
            RESULTS_DIR / "correlation" / f"p_individual_correlation_{category}.csv",
            sep=",",
        )

        dfs_correlation[f"{category}_M"] = df_M
        dfs_correlation[f"{category}_p"] = df_p

    # write results
    table_correlations = RESULTS_DIR / "table_correlations.xlsx"

    # write correlation value & p-value in table for categories
    with pd.ExcelWriter(table_correlations) as writer:
        for key, df in dfs_correlation.items():
            df.to_excel(writer, sheet_name=key, index=False)


if __name__ == "__main__":
    console.rule(style="white")
    categories = ["cyp", "ugt", "slc", "abc"]

    # create tables
    correlation_tables()

    # volcano plots
    for category in categories:
        correlation_volcano_plot(category=category)
