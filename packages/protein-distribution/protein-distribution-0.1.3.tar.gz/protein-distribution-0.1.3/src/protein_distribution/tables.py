"""Create overview tables."""

from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np
import pandas as pd
from scipy import stats

from protein_distribution import (
    DATA_MERGED_XLSX,
    DATA_XLSX,
    RESULTS_DIR,
    log,
    protein_info,
)
from protein_distribution.console import console


logger = log.get_logger(__name__)


def create_study_table(
    proteins: List[str],
    df: pd.DataFrame,
    df_groups: pd.DataFrame,
    df_individuals: pd.DataFrame,
) -> Dict[str, Dict[str, str]]:
    """Create study overview table for given list of proteins."""
    data: Dict[str, Dict[str, str]] = {}
    all_studies = df.study.unique()
    for protein in proteins:
        df_protein = df[df.protein == protein]
        studies = df_protein.study.unique()
        info = {}
        for study in all_studies:
            # get group data
            dfg = df_groups.loc[
                (df_groups.protein == protein) & (df_groups.study == study), :
            ]
            n_groups = len(dfg)

            # get individual data
            dfi = df_individuals.loc[
                (df_individuals.protein == protein) & (df_individuals.study == study), :
            ]
            n_individuals = len(dfi)

            if study in studies:  # ✓
                str_groups = f"{n_groups if n_groups else ' '}".rjust(2)
                str_individuals = f"{n_individuals if n_individuals else ' '}".ljust(2)
                info[study] = f"{str_groups}|{str_individuals}"
            else:
                info[study] = ""
        data[protein] = info

    return data


def create_study_tables(
    tables_xlsx: Path,
    drop_empty: bool = True,
    sort_by_count: bool = True,
) -> None:
    """Create all study overview tables."""
    # Load data
    df_abundance = pd.read_excel(DATA_XLSX, sheet_name="Abundance")
    df_groups = pd.read_excel(DATA_MERGED_XLSX, sheet_name="group_data")
    df_individuals = pd.read_excel(DATA_MERGED_XLSX, sheet_name="individual_data")

    proteins = protein_info.get_proteins(df_abundance, uniprot=True)
    protein_categories = protein_info.get_protein_categories(proteins)

    # create study tables
    dfs_table: Dict[str, pd.DataFrame] = {}
    for category, proteins in protein_categories.items():
        console.rule(title=category, align="left")
        data = create_study_table(
            proteins=proteins,
            df=df_abundance,
            df_groups=df_groups,
            df_individuals=df_individuals,
        )
        df = pd.DataFrame(data)
        if drop_empty:
            # remove empty rows
            df.replace("", np.nan, inplace=True)
            df.dropna(inplace=True, axis="index", how="all")
            df.replace(np.nan, "", inplace=True)

        if sort_by_count:
            # sort proteins by count
            columns = df.columns
            counts = {col: (df[col] != "").sum() for col in columns}
            sorted_value_index = reversed(np.argsort(list(counts.values())))
            sorted_columns = [columns[i] for i in sorted_value_index]
            df = df[sorted_columns]

        # transpose table for reports
        df = df.T
        df.index = df.index.set_names("protein")
        df = df.reset_index()

        dfs_table[category] = df

    with pd.ExcelWriter(tables_xlsx) as writer:
        for category in protein_categories.keys():
            dfs_table[category].to_excel(writer, sheet_name=f"{category}", index=True)


def create_protein_tables(
    tables_xlsx: Path,
) -> None:
    """Statistics for all proteins."""
    # Load data

    df_abundance = pd.read_excel(DATA_XLSX, sheet_name="Abundance")
    del df_abundance["comments"]

    proteins = protein_info.get_proteins(df_abundance, uniprot=True)
    protein_categories = protein_info.get_protein_categories(proteins)

    dfs_table: Dict[str, pd.DataFrame] = {}
    for category, proteins in protein_categories.items():
        console.rule(title=category, align="left")

        all_info = []
        for protein_id in proteins:
            # protein_id = 'CYP1A2'
            # get all individual data for protein
            df_protein = df_abundance[df_abundance.protein == protein_id]
            # subset of abundance for individual protein
            df_protein = df_protein[~pd.isnull(df_protein.value)]

            data = df_protein["value"].values
            if data is not None and len(data) > 0:
                info = calculate_info_for_protein(
                    protein_id=protein_id, df_protein=df_protein
                )
                all_info.append(info)
            else:
                console.print(f"No data for protein_id: {protein_id}")

        df = pd.DataFrame(all_info)
        # sort by mean
        df.sort_values(by=["mean"], inplace=True, ascending=False)
        dfs_table[category] = df

    with pd.ExcelWriter(tables_xlsx) as writer:
        for category in protein_categories.keys():
            dfs_table[category].to_excel(writer, sheet_name=f"{category}", index=False)
    console.log(tables_xlsx)


def merge_tables(
    tables_studies_xlsx: Path, tables_proteins_xlsx: Path, tables_all_xlsx: Path
) -> None:
    """Merge tables."""
    # Load data
    dfs_studies = pd.read_excel(tables_studies_xlsx, sheet_name=None)
    dfs_proteins = pd.read_excel(tables_proteins_xlsx, sheet_name=None)

    with pd.ExcelWriter(tables_all_xlsx) as writer:
        for category in dfs_studies:
            # merge tables
            df1 = dfs_studies[category]
            console.log(df1)
            df2 = dfs_proteins[category]
            console.log(df2)
            df = df1.merge(df2, on="protein")
            console.log(df)
            # df = df.set_index("protein")

            df.to_excel(writer, sheet_name=f"{category}", index=False)

    console.log(tables_all_xlsx)


def calculate_info_for_protein(
    protein_id: str, df_protein: pd.DataFrame
) -> Dict[str, Any]:
    """Calculate statistics for given protein.

    Heterogeneity analysis similar to Archour2014
    """
    data: np.ndarray = df_protein["value"].values

    info = {
        "protein": protein_id,
        "mean": np.mean(data),
        "mode": stats.mode(data).mode,
        "cv": np.std(data) / np.mean(data),
        "wcv": "-",
        "min": data.min(),
        "max": data.max(),
        "n": len(data),
        "unit": "pmol/mg",
        "Q": "-",
        "I^2": "-",
        "df": "-",
        "heterogeneity": "-",
    }

    # degree of freedom
    study_ids = df_protein.study.unique()
    df = len(study_ids) - 1
    info["df"] = df

    # only calculate heterogeneity if degree of freedom > 0
    if df > 0:
        # weighted mean & weighted CV
        # console.print(df_protein)
        data_sets = []
        counts = []

        for study in study_ids:
            df_study = df_protein[df_protein.study == study]
            d = df_study["value"].values
            data_sets.append(d)
            counts.append(len(d))

        counts = np.array(counts)
        means = np.array([np.mean(d) for d in data_sets])
        cvs = np.array([np.std(d) / np.mean(d) for d in data_sets])

        # info["wmean"] = np.sum(counts*means)/np.sum(counts)
        info["wcv"] = np.sum(counts * cvs) / np.sum(counts)

        # Cochranes Q
        wjs = []
        for d in data_sets:
            if np.std(d) > 0.0:
                wj = 1 / (np.std(d) ** 2)
            else:
                # only single point, use mean/value as std: Coefficient of variant = 1 assumption
                wj = 1 / (np.mean(d) ** 2)
            wjs.append(wj)
        wjs = np.array(wjs)
        varwx = np.sum(wjs * means) / np.sum(wjs)
        Q = np.sum(wjs * (means - varwx) ** 2)
        info["Q"] = Q

        # heterogeneity
        # The degree of heterogeneity can be assessed using the I2 index (eq. 6)
        # proposed by Higgins and Thompson (2002). This index provides a percentage of
        # overall heterogeneity that can be interpreted as proposed by
        # Higgins et al. (2003) as follows:
        # - around 0%, no heterogeneity, : none
        # - around 25%, low heterogeneity, : low
        # - around 50%, moderate heterogeneity, : medium
        # - and around 75%, high heterogeneity. : high
        I2 = max(0, 100 * (Q - df) / Q)
        info["I^2"] = I2
        if 0 <= I2 < 25:
            heterogeneity = "none"
        elif 25 <= I2 < 50:
            heterogeneity = "low"
        elif 50 <= I2 < 75:
            heterogeneity = "medium"
        elif 75 <= I2:
            heterogeneity = "high"

        info["heterogeneity"] = heterogeneity

    # console.print(info)
    return info


def run_all_tables() -> None:
    """Create all tables."""
    tables_studies_xlsx: Path = RESULTS_DIR / "table_studies.xlsx"
    tables_proteins_xlsx: Path = RESULTS_DIR / "table_proteins.xlsx"
    tables_all_xlsx: Path = RESULTS_DIR / "table_all.xlsx"

    create_study_tables(tables_xlsx=tables_studies_xlsx)
    create_protein_tables(tables_xlsx=tables_proteins_xlsx)

    merge_tables(
        tables_studies_xlsx,
        tables_proteins_xlsx,
        tables_all_xlsx=tables_all_xlsx,
    )


if __name__ == "__main__":
    run_all_tables()
