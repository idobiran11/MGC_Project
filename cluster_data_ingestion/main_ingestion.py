from data_scraper import DataScraper
from excel_writer import ClusterExcelWriter
from gene_files_writer import GeneFilesWriter
from scraper_config import DirectoryType, KingdomNames
from excel_write_config import IODataTypes, DirectoryData


def handler(kingdom: str):
    if kingdom == "plants":
        mibig_scraper = DataScraper(kingdom=KingdomNames.PLANT, export_location=DirectoryType.LOCAL,
                                    get_gene_data=False)
        bgc_list = mibig_scraper.get_bgc_list()
        scraper_dict = mibig_scraper.get_scraper_dict()
        ClusterExcelWriter(bgc_list=bgc_list, scraper_dict=scraper_dict,
                           excel_name=DirectoryData.PLANT_CLUSTER_EXCEL).handle_data_from_directory(
            file_type=IODataTypes.GENBANK,
            directory=DirectoryData.GENBANK_3_1)
        GeneFilesWriter(kingdom="plants").write_gene_files()

    elif kingdom == "fungi":
        mibig_scraper = DataScraper(kingdom=KingdomNames.FUNGI, export_location=DirectoryType.LOCAL,
                                    get_gene_data=False)
        bgc_list = mibig_scraper.get_bgc_list()
        scraper_dict = mibig_scraper.get_scraper_dict()
        ClusterExcelWriter(bgc_list=bgc_list, scraper_dict=scraper_dict,
                           excel_name=DirectoryData.FUNGI_CLUSTER_EXCEL).handle_data_from_directory(
            file_type=IODataTypes.GENBANK,
            directory=DirectoryData.GENBANK_3_1)
        GeneFilesWriter(kingdom="fungi").write_gene_files()

    print("Successfully created Cluster and Gene files")


if __name__ == "__main__":
    handler("fungi")
