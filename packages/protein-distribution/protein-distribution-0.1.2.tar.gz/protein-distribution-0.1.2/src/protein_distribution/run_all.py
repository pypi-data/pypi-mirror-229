"""Process all data and files for release."""
from protein_distribution.dataio import run_all_dataio
from protein_distribution.tables import run_all_tables
from protein_distribution.uniprot import query_metadata


if __name__ == "__main__":
    query_metadata()
    run_all_dataio()
    run_all_tables()
