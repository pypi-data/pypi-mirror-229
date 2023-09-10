"""Data analysis Vildhede2015."""
import numpy as np
import pandas as pd

from protein_distribution import DATA_DIR
from protein_distribution.uniprot import read_uniprot2sid


def parse_vildhede2015() -> None:
    """Parse raw data from supplementary files."""

    tsv_in_path = DATA_DIR / "Vildhede2015" / "raw" / "proteinGroups.tsv"
    xlsx_processed_path = DATA_DIR / "Vildhede2015" / "Vildhede2015_processed.xlsx"
    xlsx_out_path = DATA_DIR / "Vildhede2015" / "Vildhede2015_data.xlsx"

    if not tsv_in_path.exists():
        raise IOError(f"File does not exist: {tsv_in_path}")

    # read protein mapping
    uniprot2sid = read_uniprot2sid()

    # read data and process
    df_raw = pd.read_csv(tsv_in_path, sep="\t")
    columns = [
        "Protein IDs",  # Uniprot protein identifiers: mapping with protein_overview.xlsx
        "Protein names",
        "Gene names",
        "Proteins",  # protein count
        "Mol. weight [kDa]",  # Mr [g/mole]  # 1 dalton = 1.66053000000133E-24 gram [g].
        "Intensity",
    ]
    experiments_hepatocyte = [
        # 8 hepatocyte membrance fractions (3 repeats 1, 2, 3)
        "HA1",
        "HA2",
        "HA3",
        "HB1",
        "HB2",
        "HB3",
        "HC1",
        "HC2",
        "HC3",
        "HD1",
        "HD2",
        "HD3",
        "HE1",
        "HE2",
        "HE3",
        "HF1",
        "HF2",
        "HF3",
        "HG1",
        "HG2",
        "HG3",
        "HH1",
        "HH2",
        "HH3",
    ]
    experiments_liver = [
        # 12 liver membrane fractions
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L7",
        "L8",
        "L9",
        "L10",
        "L11",
        "L12",
    ]
    experiments = experiments_hepatocyte + experiments_liver
    columns = columns + [f"Intensity {exp}" for exp in experiments]
    print(columns)
    print("-" * 80)

    # get subset of columns
    df = df_raw[columns]
    print(df.head(10))
    print("-" * 80)

    # normalization to [mole/g (protein)]
    for exp in experiments:
        total_signal = df[f"Intensity {exp}"].sum()
        mr = df["Mol. weight [kDa]"] * 1000  # [Da] = [g/mole]

        # Calculation of protein amount from intensity data
        df[exp] = (
            (df[f"Intensity {exp}"]) / (total_signal * mr) * 1e9
        )  # [mole/g] => pmol/mg = nmol/g

    # calculate the hepatocyte mean values
    for k, key in enumerate(["A", "B", "C", "D", "E", "F", "G", "H"]):
        # calculate mean
        df[f"H{k+1}"] = df[f"H{key}1"] + df[f"H{key}2"] + df[f"H{key}3"] / 3

        # Filter by complete replicates
        zero_index = (
            (df[f"H{key}1"] == 0) | (df[f"H{key}2"] == 0) | (df[f"H{key}3"] == 0)
        )
        df.loc[zero_index, f"H{k+1}"] = 0

    # delete old keys
    df.drop([f"Intensity {key}" for key in experiments], axis=1, inplace=True)
    df.drop([f"{key}" for key in experiments_hepatocyte], axis=1, inplace=True)
    print(df.head(10))
    print("-" * 80)

    # get subset of proteins (filter protein of interests
    sids = []
    for _, row in df.iterrows():
        # FIXME: check if in place
        proteins = row["Protein IDs"]
        protein_ids = set(proteins.split(";"))
        for uniprot, sid in uniprot2sid.items():
            if uniprot in protein_ids:
                sids.append(sid)
                break
        else:
            sids.append(np.NaN)

    # print(sids)
    df["sid"] = sids

    # filter dataframe
    df_filtered = df[~pd.isna(df.sid)]

    # store results
    with pd.ExcelWriter(xlsx_processed_path) as writer:
        df_filtered.to_excel(writer, sheet_name="protein_amounts", index=False)

    # store results in our format

    data = {
        "study": "Vildhede2015",
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
        "unit": "pmol/mg",
        "comments": None,
    }
    info_items = []

    exp_columns = [
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "H7",
        "H8",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L7",
        "L8",
        "L9",
        "L10",
        "L11",
        "L12",
    ]
    for _, row in df_filtered.iterrows():
        sid = row["sid"]
        for exp in exp_columns:
            value = row[exp]
            if np.isclose(value, 0.0):
                continue
            d = {**data}
            d["individual"] = exp
            d["protein"] = sid
            d["tissue"] = "liver microsomes" if exp.startswith("L") else "hepatocyte"
            d["value"] = value
            info_items.append(d)

    df_protein = pd.DataFrame(info_items)
    with pd.ExcelWriter(xlsx_out_path) as writer:
        df_protein.to_excel(writer, sheet_name="protein_amount", index=False)


if __name__ == "__main__":
    parse_vildhede2015()
