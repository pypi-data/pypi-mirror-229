"""Uniprot information."""
import json
from typing import Dict, List

import numpy as np
import pandas as pd
import requests
import xmltodict

# from dataclasses import dataclass
from pydantic import BaseModel

from protein_distribution import (
    PROTEIN_PATH,
    SID2CATEGORY_PATH,
    UNIPROT2SID_PATH,
    UNIPROT_PATH,
)
from protein_distribution.console import console


def create_mappings() -> None:
    """Read protein mapping.

    For some CYPs no uniprot information was available. These were:
    - CYP1A6
    - CYP4F
    - CYP2C
    """

    df_proteins = pd.read_excel(
        PROTEIN_PATH,
        sheet_name="proteins",
        skiprows=[0],
        comment="#",
    )
    df_proteins.replace("-", "", inplace=True)

    uniprot2sid: Dict[str, str] = {}
    for uniprot, name in zip(df_proteins["uniprot"], df_proteins["name"]):
        if uniprot and name and uniprot != "NaN":
            uniprot2sid[uniprot] = name

    with open(UNIPROT2SID_PATH, "w") as f_json:
        json.dump(uniprot2sid, f_json, indent=2)

    sid2category = dict(zip(df_proteins["name"], df_proteins["category"]))
    with open(SID2CATEGORY_PATH, "w") as f_json:
        json.dump(sid2category, f_json, indent=2)


def read_uniprot2sid() -> Dict[str, str]:
    """Read the uniprot mapping."""
    with open(UNIPROT2SID_PATH, "r") as f_json:
        d: Dict[str, str] = json.load(f_json)
    return d


def read_sid2category() -> Dict[str, str]:
    """Read the categpry mapping."""
    with open(SID2CATEGORY_PATH, "r") as f_json:
        d: Dict[str, str] = json.load(f_json)
    return d


class UniprotMetadata(BaseModel):
    """Metadata for Uniprot Entry."""

    id: str  # P05177
    name: str  # CP1A2_HUMAN
    protein: str  # Cytochrome P450 1A2
    gene: str  # CYP1A2
    organism: str  # Homo sapiens (Human)
    # evidence: str
    function: str


class UniprotMetadataDict(BaseModel):
    """Dictionary of Uniprot Metadata entries."""

    entries: Dict[str, UniprotMetadata]


def query_uniprot_metadata(uniprot_id: str) -> UniprotMetadata:
    """Parse Metadata for protein identifier."""
    url: str = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.xml"
    console.log(f"Query: {url}")

    response = requests.get(url)
    response.raise_for_status()
    d = xmltodict.parse(response.content)

    try:
        entry = d["uniprot"]["entry"]
        organism_tokens = entry["organism"]["name"]
        protein = entry["protein"]
        if "recommendedName" in protein:
            fullname = entry["protein"]["recommendedName"]["fullName"]
        elif "submittedName" in protein:
            fullname = entry["protein"]["submittedName"]["fullName"]
        if isinstance(fullname, dict):
            fullname = fullname["#text"]

        genename = entry["gene"]["name"]
        if isinstance(genename, str):
            gene = genename
        elif isinstance(genename, list):
            gene = ", ".join(g["#text"] for g in genename)
        elif isinstance(genename, dict):
            gene = genename["#text"]

        comments = entry["comment"]
        function = ""
        if isinstance(comments, dict):
            if comments["@type"] == "function":
                comment = comments["text"]
                if isinstance(comment, str):
                    function = comment
                elif isinstance(comment, dict):
                    function = comment["#text"]
        elif isinstance(comments, list):
            for c in comments:
                if c["@type"] == "function":
                    comment = c["text"]
                    if isinstance(comment, str):
                        function = comment
                    elif isinstance(comment, dict):
                        function = comment["#text"]
                    break

        md = UniprotMetadata(
            id=uniprot_id,
            name=entry["name"],
            protein=fullname if isinstance(fullname, str) else fullname["#text"],
            gene=gene,
            organism=f"{organism_tokens[0]['#text']} ({organism_tokens[1]['#text']})",
            function=function,
        )
        # console.print(md)
    except Exception as err:
        console.print(entry)
        raise err

    return md


def query_metadata() -> UniprotMetadataDict:
    """Query Uniprot metadata via webservices."""
    uniprot2sid = read_uniprot2sid()

    mds = {}
    for uniprot_id in uniprot2sid.keys():
        mds[uniprot_id] = query_uniprot_metadata(uniprot_id)

    mddict = UniprotMetadataDict(entries=mds)
    with open(UNIPROT_PATH, "w") as f_json:
        f_json.write(mddict.model_dump_json(indent=2))

    return mddict


def read_metadata() -> UniprotMetadataDict:
    """Read uniprot metadata."""

    with open(UNIPROT_PATH, "r") as f_json:
        d = json.load(f_json)

    return UniprotMetadataDict(**d)


if __name__ == "__main__":
    # mapping
    create_mappings()
    uniprot2sid = read_uniprot2sid()
    console.print(uniprot2sid)
    sid2category = read_sid2category()
    console.print(sid2category)

    # uniprot metadata
    query_metadata()
    mddict = read_metadata()
    console.print(mddict)
