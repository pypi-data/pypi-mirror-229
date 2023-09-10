"""Prepare protein abundance data for analysis.

- data reading
- data validation
- data integration
- data normalization (e.g. unit normalization)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from protein_distribution import DATA_DIR, log, protein_info
from protein_distribution.console import console


logger = log.get_logger(__name__)


def load_study_overview() -> pd.DataFrame:
    """Load the study overview data in table."""
    df_studies = pd.read_excel(DATA_DIR / "study_overview.xlsx", sheet_name=0)
    return df_studies


def get_studies_by_status(df: pd.DataFrame, status: List[str]) -> List[str]:
    """Return list with ids of studies."""
    df_filtered = df[df.status.isin(status)]

    studies: List[str] = df_filtered.study.values
    return studies


def load_data(
    study_ids: Iterable[str], data_dir: Optional[Path] = None
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Load data for given studies."""
    if data_dir is None:
        data_dir = DATA_DIR

    study_ids_set = set(study_ids)

    for file in Path(data_dir).glob("*"):
        if file.is_dir():
            study_dir = file.name
            if study_dir not in study_ids_set:
                logger.warning(
                    f"Study directory does not exist in study_overview table '{study_dir}'."
                )

    data = {}
    for study_id in study_ids:
        console.rule(title=study_id, align="left", style="white")
        dfs: Dict[str, pd.DataFrame] = load_data_from_study(
            study_id=study_id, data_dir=data_dir
        )
        data[study_id] = dfs

    return data


def load_data_from_study(
    study_id: str, data_dir: Optional[Path] = None
) -> Dict[str, pd.DataFrame]:
    """Load data for given study.

    :param study_id: id of study
    :param data_dir: directory in which the data is located.
    """
    if data_dir is None:
        data_dir = DATA_DIR

    error = False

    # check that folder exists
    study_dir: Path = data_dir / study_id
    if not study_dir.exists():
        logger.error(f"Study directory does not exist for '{study_id}': '{study_dir}'")
        error = True
    if not study_dir.is_dir():
        logger.error(f"Study directory is not a directory: '{study_dir}'")
        error = True

    # check that PDF exist
    pdf_path = study_dir / f"{study_id}.pdf"
    if not pdf_path.exists():
        logger.error(f"PDF does not exist for '{study_id}': '{pdf_path}'")
        error = True

    # check that Excel exist
    xlsx_path = study_dir / f"{study_id}.xlsx"
    if not xlsx_path.exists():
        logger.error(f"XLSX does not exist for '{study_id}': '{xlsx_path}'")
        error = True

    # check that names are correct in folder
    for file in Path(study_dir).glob("*"):
        filename = file.name
        # don't check temporary files
        if filename.startswith(".~"):
            continue
        elif filename.startswith("~$"):
            continue

        if file.is_file():
            if not filename.startswith(f"{study_id}"):
                logger.error(f"File does not start with '{study_id}': '{file}'")
                error = True

    if error:
        console.print(f"[error]Errors in files, no data is loaded from '{study_id}'.")
        return {}
    else:
        console.print(f"[success]Files are correct for '{study_id}'.")

    # load all sheets from excel
    dfs: Dict[str, pd.DataFrame] = pd.read_excel(
        xlsx_path, sheet_name=None, comment="#"
    )

    # remove empty rows
    for df in dfs.values():
        df.dropna(how="all", axis="index", inplace=True)

    # check sheet names:
    sheet_names = dfs.keys()
    for sheet_name in sheet_names:
        if sheet_name in {"Groups", "Individuals"}:
            continue
        elif sheet_name.startswith("Tab"):
            continue
        elif sheet_name.startswith("Fig"):
            continue
        else:
            logger.error(
                f"Incorrect sheet_name in '{study_id}.xlxs': '{sheet_name}'. "
                f"Allowed names are 'Groups', 'Individuals', 'Tab*', Fig*'"
            )

    # 'Groups' sheet must exist
    if "Groups" not in sheet_names:
        logger.error(f"Groups sheet does not exist in sheets: '{sheet_names}'.")

    # Fix datatypes
    # for sheet_name in sheet_names:
    #     df = dfs[sheet_name]
    #     if sheet_name == "Groups":
    #         continue
    #     elif sheet_name == "Individuals":
    #         continue
    #     else:
    #         dfs[sheet_name] = df.astype({"group": str, "individual": str})

    # Validate individual sheets
    for sheet_name in sheet_names:
        df = dfs[sheet_name]
        # FIXME: transfer information from groups to individuals!

        if sheet_name == "Groups":
            validate_sheet_groups(df, study_id, sheet_name=sheet_name)
        elif sheet_name == "Individuals":
            validate_sheet_individuals(df, study_id, sheet_name=sheet_name)
        else:
            # add source information to the abundance table
            df.insert(loc=1, column="source", value=sheet_name)

            if len(df) == 0:
                # don't check empty data frames
                continue
            validate_sheet_data(df, study_id, sheet_name=sheet_name)

    # Validate information between sheets
    existing_groups = []
    if "Groups" in dfs:
        existing_groups = dfs["Groups"].name.unique()

    existing_individuals = []
    if "Individuals" in dfs:
        existing_individuals = dfs["Individuals"].name.unique()

    for sheet_name in sheet_names:
        if sheet_name in {"Groups", "Individuals"}:
            continue

        df = dfs[sheet_name]
        # group must exist in Groups
        for group in df.group.unique():
            if group is None:
                continue
            if group not in existing_groups:
                if not isinstance(group, str) and np.isnan(group):
                    pass
                else:
                    logger.error(
                        f"Group '{group}' from '{sheet_name}' does not exist in 'Groups'."
                    )

        # individual must exist in Individuals
        for individual in df.individual.unique():
            if individual is None:
                continue
            if individual not in existing_individuals:
                if not isinstance(individual, str) and np.isnan(individual):
                    pass
                else:
                    logger.error(
                        f"Individual '{individual}' from '{sheet_name}' does not exist in 'Individuals'."
                    )

    # console.print(dfs.keys())
    return dfs


def _check_required_columns(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    """Check required columns."""
    for field in required_columns:
        if field not in df.columns:
            logger.error(f"'{field}' column missing'.")


def _check_restricted_items(
    df: pd.DataFrame, restricted_items: Dict[str, List[str]]
) -> None:
    """Check for restricted items."""
    for key, allowed_values in restricted_items.items():
        if key in df.columns:
            for value in df[key].unique():
                if value not in allowed_values:
                    logger.error(f"{key} '{value}' must be in {allowed_values}")


def _check_measurement_types(df: pd.DataFrame, info_dict: Dict[str, Dict]) -> None:
    """Check values which are allowed for a given measurement type."""
    for _, row in df.iterrows():
        mtype = row.measurement_type
        if mtype not in info_dict:
            logger.error(f"Measurement type '{mtype}' is not supported.")
        else:
            info = info_dict[mtype]

            if info["dtype"] == "categorical":
                if not row.choice:
                    logger.error(f"'choice' must be set for '{mtype}' in '{row}'")
                else:
                    choices = info["choices"]
                    if choices and row.choice not in choices:
                        logger.error(
                            f"choice '{row.choice}' for '{mtype}' not in allowed choices: {choices} in '{row}'"
                        )
                for col in ["mean", "sd", "min", "max", "max", "median"]:
                    if col in row and row[col] and not np.isnan(row[col]):
                        logger.error(
                            f"'{col}' can not be set for categorical '{mtype}' in '{row}'."
                        )

            elif info["dtype"] == "numerical":
                for col in ["choice"]:
                    if (
                        row[col]
                        and not isinstance(row[col], str)
                        and not np.isnan(row[col])
                    ):
                        logger.error(
                            f"'{col}' can not be set for numerical '{mtype}' in '{row}'."
                        )
                for col in ["unit"]:
                    if not row[col]:
                        logger.error(
                            f"'{col}' is required for numerical '{mtype}' in '{row}'."
                        )
                    if not isinstance(row[col], str) and np.isnan(row[col]):
                        logger.error(
                            f"'{col}' is required for numerical '{mtype}' in '{row}'."
                        )


def _check_required_fields(df: pd.DataFrame, required_fields: Iterable[str]) -> None:
    """Check for required fields."""
    for field in required_fields:
        if field in df.columns:
            na_count = df[field].isnull().sum()
            if na_count > 0:
                logger.error(f"'{field}' is required, but some values are empty.")


def _check_numeric_fields(df: pd.DataFrame, numeric_fields: Iterable[str]) -> None:
    """Check that fields are numeric."""
    for field in numeric_fields:
        if field in df.columns:
            if not is_numeric_dtype(df[field]):
                logger.error(f"'{field}' must be numeric, but is {df[field].dtype}")


def validate_sheet(df: pd.DataFrame, study_id: str, sheet_name: str) -> None:
    """Validate generic sheet."""

    # study column must exist and must be study_id
    if "study" not in df.columns:
        logger.error(f"'study' column missing in '{study_id}_{sheet_name}'.")
    else:
        study_values = df.study.unique()
        if len(study_values) == 1:
            if study_values[0] != study_id:
                logger.error(
                    f"'study' column must be '{study_id}', but '{study_values[0]}'."
                )
        elif len(study_values) > 1:
            logger.error(
                f"'study' column must be '{study_id}', but multiple values found: "
                f"'{study_values}'"
            )


person_measurement_types = {
    "species": {
        "required": True,
        "dtype": "categorical",
        "choices": {
            "homo sapiens",
            "primates",
            "canis familiaris",
            "rattus norvegicus",
            "mammalia",
        },
    },
    "age": {"required": True, "dtype": "numerical", "unit": "yr", "min": 0, "max": 150},
    "weight": {
        "required": True,
        "dtype": "numerical",
        "unit": "kg",
        "min": 0,
        "max": 200,
    },
    "bmi": {
        "required": True,
        "dtype": "numerical",
        "unit": "kg/m^2",
        "min": 5,
        "max": 45,
    },
    "ethnicity": {
        "required": True,
        "dtype": "categorical",
        "choices": {
            "NR",
            "african",
            "african american",
            "arab american",
            "american indian",
            "asian",
            "korean",
            "japanese",
            "MF" "thai",
            "caucasian",
            "chinese",
            "hispanic",
            "white new zealanders",
            "asian indian",
            "afro trinidadians",
            "indo trinidadians",
            "black",
        },
    },
    "healthy": {
        "required": True,
        "dtype": "categorical",
        "choices": {"NR", "Y", "N", "YN"},
    },
    "sex": {
        "required": True,
        "dtype": "categorical",
        "choices": {"NR", "M", "F", "MF"},
    },
    "smoking": {
        "required": True,
        "dtype": "categorical",
        "choices": {"NR", "Y", "N", "YN"},
    },
    "alcohol": {
        "required": True,
        "dtype": "categorical",
        "choices": {"NR", "Y", "N", "YN"},
    },
    # not required
    "height": {
        "required": False,
        "dtype": "numerical",
        "unit": "cm",
        "min": 0,
        "max": 250,
    },
    "disease": {
        "required": False,
        "dtype": "categorical",
        "choices": {
            "NR",
            "hepatocellular cancer",
            "hepatocellular carcinoma",
            "hepatic cholangiocarcinoma",
            "adenocarcinoma",
            "cholangiocarcinoma",
            "cavernous hemangioma of liver",
            "intrahepatic stone",
            "gallbladder cancer",
            "papillary carcinoma",
            "diabetes",
            "cytostatic treatment",
            "gynecological cancer",
            "colorectal cancer",
            "metastatic carcinoma",
            "cholelithiasis",
        },
    },
    "cause of death": {"required": False, "dtype": "categorical", "choices": None},
    "medical history": {"required": False, "dtype": "categorical", "choices": None},
    "medication": {"required": False, "dtype": "categorical", "choices": None},
    "treatment": {"required": False, "dtype": "categorical", "choices": None},
    "anaesthetic": {"required": False, "dtype": "categorical", "choices": None},
    "liver pathology": {"required": False, "dtype": "categorical", "choices": None},
    "postmortem time": {"required": False, "dtype": "numerical", "unit": "min"},
}


def validate_sheet_groups(df: pd.DataFrame, study_id: str, sheet_name: str) -> None:
    """Validate group sheet."""
    console.print(f"validate_sheet_groups: {sheet_name}")
    validate_sheet(df=df, study_id=study_id, sheet_name=sheet_name)

    # check required columns
    required_columns = {
        "study",
        "name",
        "group_count",
        "parent",
        "measurement_type",
        "count",
        "substance",
        "choice",
        "mean",
        "sd",
        "min",
        "max",
        "unit",
        "comments",
    }
    _check_required_columns(df, required_columns=required_columns)

    restricted_items = {
        "measurement_type": list(person_measurement_types.keys()),
    }
    _check_restricted_items(df, restricted_items=restricted_items)

    _check_measurement_types(df, info_dict=person_measurement_types)

    # check for "all" group
    groups = df["name"].unique()
    if "all" not in groups:
        logger.error("Group 'all' missing")

    # check that parent is set
    for _, row in df.iterrows():
        if row["name"] == "all":
            continue
        if not row.parent or (isinstance(row.parent, float) and np.isnan(row.parent)):
            logger.error(f"'parent' group must be set for group '{row['name']}'")

    # check that count is set
    for _, row in df.iterrows():
        if not row["count"]:
            logger.error(f"'count' must be set in {row}")

    # FIXME: check the required fields for groups
    # console.print(df)
    # for group in df.name.unique():
    #     df_group = df[df.name == group]
    #     mtypes = df_group.measurement_type.unique()
    #     for mtype, mtype_info in person_measurement_types.items():
    #         required = mtype_info["required"]
    #         if required and not mtype in mtypes:
    #             logger.error(f"measurement_type '{mtype}' missing for group '{group}'")


def validate_sheet_individuals(
    df: pd.DataFrame, study_id: str, sheet_name: str
) -> None:
    """Validate individual sheet."""
    console.print(f"validate_sheet_individuals: {sheet_name}")
    validate_sheet(df=df, study_id=study_id, sheet_name=sheet_name)
    required_columns = [
        "study",
        "name",
        "group",
        "measurement_type",
        "substance",
        "choice",
        "value",
        "unit",
        "comments",
    ]
    _check_required_columns(df, required_columns=required_columns)

    restricted_items = {
        "measurement_type": list(person_measurement_types.keys()),
    }
    _check_restricted_items(df, restricted_items=restricted_items)

    _check_measurement_types(df, info_dict=person_measurement_types)

    # check that group is set
    for _, row in df.iterrows():
        if not row["group"]:
            logger.error(f"'group' must be set in {row}")


def validate_sheet_data(df: pd.DataFrame, study_id: str, sheet_name: str) -> None:
    """Validate data sheet."""
    console.print(f"validate_sheet_data: {sheet_name}")
    validate_sheet(df=df, study_id=study_id, sheet_name=sheet_name)

    # check required columns
    required_columns = [
        "study",
        "count",
        "measurement_type",
        "protein",
        "tissue",
        "method",
        "value",
        "mean",
        "sd",
        "median",
        "min",
        "max",
        "cv",
        "cv_unit",
        "mad",
        "unit",
        "comments",
    ]
    _check_required_columns(df, required_columns=required_columns)

    restricted_items = {
        "tissue": [
            "liver microsomes",
            "liver plasma membrane",
            "liver membrane",
            "kidney membrane",
            "hepatocyte",
            "jejunum",
            "duodenum",
        ],
        "measurement_type": ["abundance"],
    }
    _check_restricted_items(df, restricted_items=restricted_items)

    required_fields = [
        "study",
        "count",
        "measurement_type",
        "protein",
        "tissue",
        "unit",
    ]
    _check_required_fields(df, required_fields=required_fields)

    # test that either group or individual is set
    if "group" in df.columns and "individual" in df.columns:
        # check that both are zero
        item_count = (~df["group"].isnull()).sum() + (~df["individual"].isnull()).sum()
        if item_count != len(df):
            logger.error(
                "either 'individual' or 'group' must be set, but some values are empty or have both."
            )

    # check that fields are numeric
    numeric_fields = [
        "value",
        "mean",
        "sd",
        "median",
        "min",
        "max",
        "cv",
        "mad",
        "count",
    ]
    _check_numeric_fields(df, numeric_fields=numeric_fields)


def merge_tables(
    data: Dict[str, pd.DataFrame], sids: List[str], excel_path: Optional[Path]
) -> pd.DataFrame:
    """Merge tables in a single table."""

    dfs: List[pd.DataFrame] = []
    for sid in sids:
        df = data[sid]
        df["sid"] = sid
        dfs.append(data[sid])

    df_merged = pd.concat(dfs)
    df_merged.to_excel(excel_path, sheet_name="abundance", index=False)
    return df_merged


def process_all_data(
    data_xlsx: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Process all study data."""
    # get the study ids from the study_overview table
    df_studies = load_study_overview()
    study_ids = sorted(df_studies.study.values)

    excluded_ids: List[str] = []
    study_ids = [sid for sid in study_ids if sid not in excluded_ids]
    # study_ids = ["Achour2014"]

    console.print(study_ids)

    # try to load individual study
    # study_id = study_ids[0]
    # data = dataio.load_data_from_study(study_id)

    # try to load all studies
    data: Dict[str, Dict[str, pd.DataFrame]] = load_data(study_ids=study_ids)

    # at the end of the data reading we have 3 large tables
    # merge table:
    # 1. Groups data
    # 2. Individual data
    # 3. Abundance data
    dfs_groups = []
    dfs_individuals = []
    dfs_abundance = []
    for _, data_dict in data.items():
        for sheet_name, df in data_dict.items():
            if sheet_name == "Groups":
                dfs_groups.append(df)
            elif sheet_name == "Individuals":
                dfs_individuals.append(df)
            else:
                dfs_abundance.append(df)

    df_groups = pd.concat(dfs_groups)
    df_individuals = pd.concat(dfs_individuals)
    df_abundance = pd.concat(dfs_abundance)

    # unit normalization
    for unit in df_abundance["unit"].unique():
        if unit != "pmol/mg":
            if unit == "fmol/mug":
                factor_unit = 1.0
            elif unit == "fmol/µg":
                factor_unit = 1.0
            elif unit == "amol/mug":
                factor_unit = 1000.0  # FIXME: check this
            elif unit == "nmol/mg":
                factor_unit = 1000.0
            elif unit == "fmol/g":
                factor_unit = 1000.0  # FIXME: check this
            else:
                logger.error(f"Unsupported unit: '{unit}'")
                continue

            row_index = df_abundance.unit == unit
            for key in [
                "value",
                "mean",
                "sd",
                "se",
                "median",
                "min",
                "max",
                "mean_pm_sd",
            ]:
                df_abundance.loc[row_index, key] = (
                    df_abundance[row_index][key] * factor_unit
                )
            df_abundance.loc[row_index, "unit"] = "pmol/mg"

    # calculate SD from SE
    row_index = pd.isnull(df_abundance["sd"]) & ~pd.isnull(df_abundance["se"])
    df_abundance.loc[row_index, "sd"] = df_abundance[row_index]["se"] * np.sqrt(
        df_abundance[row_index]["count"]
    )

    # calculate SD from CV
    row_index = (
        pd.isnull(df_abundance["sd"])
        & ~pd.isnull(df_abundance["cv"])
        & (df_abundance["cv_unit"] == "percent")
    )
    df_abundance.loc[row_index, "sd"] = (
        df_abundance[row_index]["cv"] / 100.0 * df_abundance[row_index]["mean"]
    )

    # set value for individuals from mean
    row_index = (
        (pd.isnull(df_abundance["value"]))
        & (~pd.isnull(df_abundance["individual"]))
        & (~pd.isnull(df_abundance["mean"]))
    )
    df_abundance.loc[row_index, "value"] = df_abundance[row_index]["mean"]
    # remove mean
    df_abundance.loc[row_index, "mean"] = np.NaN
    df_abundance.loc[row_index, "sd"] = np.NaN

    # filter empty rows
    df_abundance.reset_index(inplace=True, drop=True)
    row_index = (pd.isnull(df_abundance["value"])) & (pd.isnull(df_abundance["mean"]))
    df_abundance.drop(df_abundance[row_index].index, inplace=True)

    # remove unnecessary columns
    for col in [
        "heterogeneity",
        "q",
        "r2",
        "r2_unit",
        "mean_pm_sd",
        "percent_total_cyp",
        "max_over_min",
        "max/min",
        "variance",
        "q1",
        "q3",
        "logmean",
        "logmean_unit",
        "sample_name",
        "vmax",
        "vmax_unit",
        # additional columns
        "mad",
        "cv",
        "cv_unit",
        "median",
        "se",
        "method",
        "min",
        "max",
    ]:
        if col in df_abundance.columns:
            df_abundance.drop(columns=[col], inplace=True)

    with pd.ExcelWriter(data_xlsx) as writer:
        df_groups.to_excel(writer, sheet_name="Groups", index=False)
        df_individuals.to_excel(writer, sheet_name="Individuals", index=False)
        df_abundance.to_excel(writer, sheet_name="Abundance", index=False)

    return df_groups, df_individuals, df_abundance


def filter_data(
    data_raw_xlsx: Path,
    data_xlsx: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Filter data.

    Reduce to data with sufficient data points.
    """

    df_groups = pd.read_excel(data_raw_xlsx, sheet_name="Groups")
    df_individuals = pd.read_excel(data_raw_xlsx, sheet_name="Individuals")
    df_abundance = pd.read_excel(data_raw_xlsx, sheet_name="Abundance")

    # filter proteins which are not in human
    count_start = len(df_abundance)

    proteins_nonhuman = df_abundance[
        df_abundance.protein.str.contains("_")
    ].protein.unique()
    df_abundance = df_abundance[~df_abundance.protein.str.contains("_")]

    console.print(
        f"Filtered '{count_start - len(df_abundance)}' non-human entries: '{proteins_nonhuman}'"
    )

    # Filter minimal count of proteins
    value_cutoff = 10
    proteins = df_abundance.protein.unique()
    for pid in proteins:
        if df_abundance[df_abundance.protein == pid].value.count() < value_cutoff:
            console.print(f"Filtered protein '{pid}' with < {value_cutoff} values.")
            df_abundance = df_abundance[~(df_abundance.protein == pid)]

    with pd.ExcelWriter(data_xlsx) as writer:
        df_groups.to_excel(writer, sheet_name="Groups", index=False)
        df_individuals.to_excel(writer, sheet_name="Individuals", index=False)
        df_abundance.to_excel(writer, sheet_name="Abundance", index=False)

    return df_groups, df_individuals, df_abundance


def process_merge_sheets(data_xlsx: Path, merged_xlsx: Path) -> None:
    """Merge group/individual information with abundance.

    - [ ] format sheets
    - [ ] create merged table with subject/group information
    - [ ] calculate group characteristica from individual characteristica and viceversa
    """
    df_groups = pd.read_excel(data_xlsx, sheet_name="Groups")
    df_groups.insert(
        0, column="sid", value=(df_groups["study"] + "_" + df_groups["name"])
    )

    df_individuals = pd.read_excel(data_xlsx, sheet_name="Individuals")
    df_individuals.insert(
        0, column="sid", value=(df_individuals["study"] + "_" + df_individuals["name"])
    )

    df_abundance = pd.read_excel(data_xlsx, sheet_name="Abundance")

    # get individual abundance
    data_individuals: pd.DataFrame = df_abundance.loc[
        ~pd.isnull(df_abundance["value"]), :
    ]
    data_individuals = data_individuals.copy()
    data_individuals.drop(columns=["group", "mean", "sd", "comments"], inplace=True)
    data_individuals.insert(
        0,
        column="sid",
        value=(data_individuals["study"] + "_" + data_individuals["individual"]),
    )

    # get group abundance
    data_groups: pd.DataFrame = df_abundance.loc[~pd.isnull(df_abundance["mean"]), :]
    data_groups = data_groups.copy()
    data_groups.drop(columns=["individual", "value", "comments"], inplace=True)
    data_groups.insert(
        0, column="sid", value=(data_groups["study"] + "_" + data_groups["group"])
    )

    # TODO: processing of group/individual information still missing
    individual_data = {}
    mtypes = {"species", "sex", "age", "bmi", "smoking", "alcohol", "ethnicity"}
    for sid in df_individuals.sid.unique():
        individual_data[sid] = {
            "sid": sid,
            "species": "homo sapiens",
            "sex": "NR",
            "age": np.NaN,
            "age_group": "NR",
            "bmi": np.NaN,
            "bmi_group": "NR",
            "smoking": "NR",
            "alcohol": "NR",
            "ethnicity": "NR",
        }

    # sex, age, bmi, smoking, alcohol, ethnicity
    for _, row in df_individuals.iterrows():
        mtype = row.measurement_type
        if mtype not in mtypes:
            continue

        if mtype in {"species", "sex", "smoking", "alcohol", "ethnicity"}:
            individual_data[row.sid][mtype] = row.choice
        elif mtype in {"age", "bmi"}:
            individual_data[row.sid][mtype] = row.value

            # Major adult BMI classifications are
            # - underweight: bmi < 18.5 kg/m2
            # - normal weight: 18.5 <= bmi < 25)
            # - overweight: 25 <= bmi < 30)
            # - obese: 30 <= bmi
            if mtype == "bmi":
                if row.value < 18.5:
                    bmi_group = "underweight"
                elif 18.5 <= row.value < 25:
                    bmi_group = "normal weight"
                elif 25 <= row.value < 30:
                    bmi_group = "overweight"
                elif 30 <= row.value:
                    bmi_group = "obese"
                elif np.isnan(row.value):
                    bmi_group = "NR"

                individual_data[row.sid]["bmi_group"] = bmi_group

            # Major age classifications are
            if mtype == "age":
                if row.value < 18:
                    age_group = "adolescent"
                elif 18 <= row.value < 35:
                    age_group = "adult"
                elif 35 <= row.value < 65:
                    age_group = "middle aged"
                elif 65 <= row.value:
                    age_group = "elderly"
                elif np.isnan(row.value):
                    age_group = "NR"

                individual_data[row.sid]["age_group"] = age_group

    df_characteristica = pd.DataFrame(individual_data.values())
    data_individuals = data_individuals.merge(df_characteristica, on="sid")

    # process correlation information for group data
    corr_data: Dict[str, Dict[str, Any]] = {}
    corr_count: Dict[str, int] = {}
    for _, row in data_groups.iterrows():
        # key = f"{row['study']}_{row['source']}_{row['group']}_{row['tissue']}"
        key = f"{row['study']}_{row['group']}_{row['tissue']}"
        if key in corr_data:
            d = corr_data[key]
        else:
            d = {
                "study": row["study"],
                # "source": row["source"],
                "group": row["group"],
                "tissue": row["tissue"],
            }
        d[row["protein"]] = row["mean"]
        d[f'{row["protein"]}_sd'] = row["sd"]
        corr_count[key] = corr_count.get(key, 0) + 1
        corr_data[key] = d

    # filter data to entries with at least two proteins
    corr_data = {k: v for k, v in corr_data.items() if corr_count[k] > 1}
    correlation_groups = pd.DataFrame(corr_data.values())
    protein_columns = [
        c
        for c in correlation_groups.columns
        if c not in ["study", "source", "group", "tissue"]
    ]
    # filter to proteins with uniprot
    columns = ["study", "group", "tissue"] + sorted(protein_columns)
    correlation_groups = correlation_groups[columns]

    # process correlation information for individual data
    corr_data = {}
    corr_count = {}
    for _, row in data_individuals.iterrows():
        key = f"{row['study']}_{row['individual']}_{row['tissue']}"
        if key in corr_data:
            d = corr_data[key]
        else:
            d = {
                "study": row["study"],
                "individual": row["individual"],
                "tissue": row["tissue"],
            }
        d[row["protein"]] = row["value"]
        corr_count[key] = corr_count.get(key, 0) + 1
        corr_data[key] = d

    corr_data = {k: v for k, v in corr_data.items() if corr_count[k] > 1}
    correlation_individuals = pd.DataFrame(corr_data.values(), index=corr_data.keys())
    # order columns
    protein_columns = [
        c
        for c in correlation_individuals.columns
        if c not in ["study", "source", "individual", "tissue"]
    ]

    proteins = protein_info.get_proteins(df_abundance, uniprot=True)
    protein_columns = [p for p in protein_columns if p in set(proteins)]
    columns = ["study", "individual", "tissue"] + sorted(protein_columns)
    correlation_individuals = correlation_individuals[columns]
    # at least 5 values required
    for protein_id in protein_columns:
        if correlation_individuals[protein_id].count() < 10:
            console.log(f"Not enough values, drop: {protein_id}")
            correlation_individuals.drop(columns=[protein_id], inplace=True)

    protein_categories = protein_info.get_protein_categories(proteins)

    # write data
    with pd.ExcelWriter(merged_xlsx) as writer:
        data_groups.to_excel(writer, sheet_name="group_data", index=False)
        data_individuals.to_excel(writer, sheet_name="individual_data", index=False)
        correlation_groups.to_excel(writer, sheet_name="group_correlation", index=False)
        correlation_individuals.to_excel(
            writer, sheet_name="individual_correlation", index=False
        )

        meta_cols = ["study", "individual", "tissue"]
        for category, protein_ids in protein_categories.items():
            protein_cols = [
                c for c in correlation_individuals.columns if c in protein_ids
            ]
            # find empty rows
            df_tmp_proteins = correlation_individuals[protein_cols]
            empty_row_idx = df_tmp_proteins.isna().all(axis="columns")

            all_cols = meta_cols + protein_cols
            df_tmp = correlation_individuals[all_cols]
            df_tmp = df_tmp[~empty_row_idx]
            df_tmp.to_excel(writer, sheet_name=f"individual_correlation_{category}")

    return None


def prepare_normalization_sheets(normalization_xlsx: Path, merged_xlsx: Path) -> None:
    """Prepare data for normalization."""
    console.rule(title="XLSX for normalization", align="left", style="white")
    df_group_data: pd.DataFrame = pd.read_excel(merged_xlsx, sheet_name="group_data")
    df_individual_data: pd.DataFrame = pd.read_excel(
        merged_xlsx, sheet_name="individual_data"
    )

    # FIXME: bugfix of additional column, this should never be written
    del df_group_data["protein.1"]
    del df_individual_data["protein.1"]

    # FIXME: calculate a dset_id for now (improve this)
    for df in [df_group_data, df_individual_data]:
        df.insert(1, column="dset_id", value=(df["study"] + "_" + df["source"]))

    # FIXME: format the excel automatically
    with pd.ExcelWriter(normalization_xlsx) as writer:
        df_individual_data.to_excel(writer, sheet_name="individual_data", index=False)
        df_group_data.to_excel(writer, sheet_name="group_data", index=False)

    console.print(normalization_xlsx)


def run_all_dataio() -> None:
    """Run all processing steps."""
    from protein_distribution import (
        DATA_MERGED_XLSX,
        DATA_NORMALIZATION_XLSX,
        DATA_RAW_XLSX,
        DATA_XLSX,
    )

    # process all data
    process_all_data(data_xlsx=DATA_RAW_XLSX)

    # apply filters
    df_groups, df_individuals, df_abundance = filter_data(
        data_raw_xlsx=DATA_RAW_XLSX, data_xlsx=DATA_XLSX
    )

    # show categories for data
    proteins = protein_info.get_proteins(df_abundance, uniprot=True)
    protein_categories = protein_info.get_protein_categories(proteins)
    console.rule(style="white")
    console.print(protein_categories)
    console.rule(style="white")

    # merge sheets for data
    process_merge_sheets(data_xlsx=DATA_XLSX, merged_xlsx=DATA_MERGED_XLSX)
    # subset of data for normalization
    prepare_normalization_sheets(
        normalization_xlsx=DATA_NORMALIZATION_XLSX, merged_xlsx=DATA_MERGED_XLSX
    )


if __name__ == "__main__":
    run_all_dataio()
