"""Parse data from supplentary file of Wegler2022."""
from pathlib import Path

import numpy as np
import pandas as pd

from protein_distribution import DATA_DIR


def parse_data() -> None:
    """Parse Wegler2022 proteomics data."""
    xlsx_in_path = DATA_DIR / "Wegler2022" / "Wegler2022_supplement_2.xlsx"
    xlsx_out_path = DATA_DIR / "Wegler2022" / "Wegler2022_data.xlsx"

    if not xlsx_in_path.exists():
        raise IOError(f"File does not exist: {xlsx_in_path}")

    dfs = {}
    subject_prefixes = ["Jejunum", "Liver", "CholLiver"]
    for k, sheet_name in enumerate(
        [
            "Proteins_Jejunum_Obese",
            "Proteins_Liver_Obese",
            "Proteins_Liver_NonObese",
        ]
    ):
        subject_prefix = subject_prefixes[k]
        print(subject_prefix)

        df = pd.read_excel(xlsx_in_path, sheet_name=sheet_name, skiprows=[0])
        print(df.head())

        column_subset = {}
        for column in df.columns:
            if column == "Gene.names":
                column_subset[column] = "gene"

            elif column.startswith(subject_prefix):
                tokens = column.split(" ")
                k = tokens[1]
                if sheet_name in ["Proteins_Jejunum_Obese", "Proteins_Liver_Obese"]:
                    column_subset[column] = f"Obese{k}"
                elif sheet_name in ["Proteins_Liver_NonObese"]:
                    column_subset[column] = f"Nonobese{k}"

        # create subset
        df_filtered = df[list(column_subset.keys())]

        # rename columns
        df_filtered.rename(columns=column_subset, inplace=True)
        # set index
        df_filtered.set_index(keys=["gene"], inplace=True)

        print(df_filtered.head())

        # TabA, TabB, TabC
        data = {
            "study": "Wegler2022",
            "group": None,
            "individual": None,  # fill this,
            "count": 1,
            "measurement_type": "abundance",
            "protein": None,  # fill this
            "tissue": None,  # fill this (liver microsomes, jejunun),
            "method": None,
            "value": None,  # fill this
            "mean": None,
            "sd": None,
            "median": None,
            "min": None,
            "max": None,
            "mad": None,
            "cv": None,
            "cv_unit": None,
            "unit": "fmol/µg",
            "comments": None,
        }
        info_items = []

        for gene, row in df_filtered.iterrows():
            # FIXME: this must be done via the protein idenifiers
            if (
                gene.startswith("CYP")
                or gene.startswith("UGT")
                or gene.startswith("ABC")
                or gene.startswith("SLC")
            ):
                if ";" in gene:
                    # skip combined proteins
                    continue
                for column in df_filtered.columns:
                    value = row[column]
                    if np.isnan(value):
                        # skip empty values
                        continue
                    d = {**data}
                    d["individual"] = column
                    d["protein"] = gene
                    d["tissue"] = (
                        "jejunum" if "Jejunum" in sheet_name else "liver microsomes"
                    )
                    d["value"] = row[column]
                    info_items.append(d)

        df_protein = pd.DataFrame(info_items)
        dfs[sheet_name] = df_protein
        print(df_protein.to_string())

    tabs = ["TabA", "TabB", "TabC"]
    with pd.ExcelWriter(xlsx_out_path) as writer:
        for k, sheet_name in enumerate(dfs):
            df = dfs[sheet_name]
            df.to_excel(writer, sheet_name=tabs[k], index=False)


if __name__ == "__main__":
    parse_data()
