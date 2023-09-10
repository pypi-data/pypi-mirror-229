"""Module for retrieving and working with protein information."""

from typing import Dict, List

import pandas as pd

from protein_distribution import PROTEIN_PATH, log
from protein_distribution.console import console
from protein_distribution.uniprot import read_uniprot_mapping


logger = log.get_logger(__name__)


def get_proteins_uniprot(proteins: List[str]) -> List[str]:
    """Filter a list of protein identifiers.

    Only returns identifiers with uniprot entry.
    """
    # get subset of proteins and filter for entries with uniprot id
    uniprot2sid = read_uniprot_mapping()
    sid2uniprot = {v: k for k, v in uniprot2sid.items()}

    proteins_uniprot = [p for p in proteins if p in sid2uniprot]
    # proteins_filtered = [p for p in proteins if p not in sid2uniprot]
    # console.print(f"Filtered UniProt: {proteins_filtered}")

    return proteins_uniprot


def get_proteins(df_abundance: pd.DataFrame, uniprot: bool = True) -> List[str]:
    """Get unique list of protein identifiers from Abundance DataFrame."""
    proteins = sorted(df_abundance["protein"].unique())
    if uniprot:
        proteins = get_proteins_uniprot(proteins)
    return proteins


def get_protein_categories(proteins: List[str]) -> Dict[str, List[str]]:
    """Categorizes proteins in classes.

    Expects proteins with uniprot identifier.
    """
    df_proteins = pd.read_excel(
        PROTEIN_PATH, sheet_name="proteins", skiprows=[0], comment="#"
    )

    sid2category = dict(zip(df_proteins["name"], df_proteins["category"]))
    d: Dict[str, List[str]] = {}
    for sid in proteins:
        category = sid2category[sid]
        if category in d:
            d[category].append(sid)
        else:
            d[category] = [sid]

    return d
