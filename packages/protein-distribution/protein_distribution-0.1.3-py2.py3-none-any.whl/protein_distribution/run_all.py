"""Process all data and files for release."""
from protein_distribution.dataio import run_all_dataio
from protein_distribution.tables import run_all_tables
from protein_distribution.uniprot import create_mappings, query_metadata


if __name__ == "__main__":
    # create JSON files
    create_mappings()
    query_metadata()

    # process data files
    run_all_dataio()
    # create tables
    run_all_tables()
