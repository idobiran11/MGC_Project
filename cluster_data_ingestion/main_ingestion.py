from data_scraper import DataScraper
from excel_writer import ClusterExcelWriter
from gene_files_writer import GeneCompoundFilesWriter
from scraper_config import DirectoryType, KingdomNames
from excel_write_config import IODataTypes, DirectoryData
import logging
from uniprot_ingestion import UniProtApiIngestion, KEGGIngestion, GeneDBNames, uniprot_plant_handler

logging.basicConfig(format=' %(asctime)s | %(levelname)s | %(message)s', level=logging.INFO)


def handler(kingdom: str = "plants"):
    if kingdom == "plants":
        mibig_scraper = DataScraper(kingdom=KingdomNames.PLANT, export_location=DirectoryType.LOCAL,
                                    get_gene_data=False)
        bgc_list = mibig_scraper.get_bgc_list()
        scraper_dict = mibig_scraper.get_scraper_dict()
        ClusterExcelWriter(bgc_list=bgc_list, scraper_dict=scraper_dict,
                           excel_name=DirectoryData.PLANT_CLUSTER_EXCEL).handle_data_from_directory(
            file_type=IODataTypes.GENBANK)
        GeneCompoundFilesWriter(kingdom="plants").write_gene_and_compounds_files()
        uniprot_plant_handler()

    elif kingdom == "fungi":
        mibig_scraper = DataScraper(kingdom=KingdomNames.FUNGI, export_location=DirectoryType.LOCAL,
                                    get_gene_data=False)
        bgc_list = mibig_scraper.get_bgc_list()
        scraper_dict = mibig_scraper.get_scraper_dict()
        ClusterExcelWriter(bgc_list=bgc_list, scraper_dict=scraper_dict,
                           excel_name=DirectoryData.FUNGI_CLUSTER_EXCEL).handle_data_from_directory(
            file_type=IODataTypes.GENBANK)
        GeneCompoundFilesWriter(kingdom="fungi").write_gene_and_compounds_files()
        # No handler for fungi uniprot data

    logging.info("Successfully created Cluster and Gene files")


if __name__ == "__main__":
    handler()
