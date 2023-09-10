"""pymetadata - Python utilities for metadata."""
from pathlib import Path

__author__ = "Matthias Koenig"
__version__ = "0.1.2"


program_name: str = "protein-distribution"

BASE_DIR = Path(__file__).parent.parent.parent

# data for analysis (not distributed)
DATA_DIR = BASE_DIR / "data"
PROTEIN_PATH = DATA_DIR / "protein_overview.xlsx"

# results of analysis
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# resources (distributed)
RESOURCES_DIR = Path(__file__).parent / "resources"

UNIPROT_PATH = RESOURCES_DIR / "uniprot.json"
UNIPROT_MAPPING_PATH = RESOURCES_DIR / "uniprot_mapping.json"

DATA_RAW_XLSX = RESOURCES_DIR / "data_raw.xlsx"
DATA_XLSX = RESOURCES_DIR / "data.xlsx"
DATA_MERGED_XLSX = RESOURCES_DIR / "data_merged.xlsx"
DATA_NORMALIZATION_XLSX = RESOURCES_DIR / "data_normalization.xlsx"
