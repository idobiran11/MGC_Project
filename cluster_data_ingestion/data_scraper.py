import time
from cluster_data_ingestion.scraper_config import KingdomNames, DirectoryType, MibigQueryData
from cluster_data_ingestion.excel_write_config import IODataTypes, DirectoryData
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from cluster_data_ingestion.excel_writer import ClusterExcelWriter


class DataScraper:
    """
    Class that scrapes data from Web to excel files
    """

    def __init__(self, kingdom: str, export_location: str,
                 get_gene_data: bool, query_data=MibigQueryData):
        """
        :param kingdom: str- kingdom to extract from Mibig
        :param get_gene_data: bool- whether to write to gene files
        :param export_location: export tables to cluster or local
        :param query_data: mibig, ... Enum of relevant data
        """
        self.bgc_words = []
        self.get_gene_data = get_gene_data
        self.export_location = export_location
        self.kingdom = kingdom
        self.query_data = query_data
        self.output_dict = dict()
        if self.query_data == MibigQueryData:
            self._initialize_selenium()
            self._mibig_run_query()

    def _initialize_selenium(self):
        """
        initializes selenium
        experimental option: uses browser open even if completed
        :return:
        """
        self.options = Options()
        self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.driver.implicitly_wait(10)

    def _mibig_run_query(self):
        self.driver.get(self.query_data.URL)
        self.driver.maximize_window()
        self._mibig_load_cluster_table()
        self._mibig_extract_data_from_table()
        self.driver.close()

    def _mibig_load_cluster_table(self):
        build_query_button = self.driver.find_element(By.XPATH, self.query_data.BUILD_QUERY)
        build_query_button.click()
        input_element = Select(self.driver.find_element(By.XPATH, self.query_data.DROP_DOWN))

        input_element.select_by_visible_text(self.query_data.DD_KINGDOM)
        search_input = self.driver.find_element(By.XPATH, self.query_data.QUERY_NAME)
        search_input.send_keys(self.kingdom)
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)
        final_button = self.driver.find_element(By.XPATH, self.query_data.FINAL_QUERY_BUTTON)
        final_button.click()
        time.sleep(2)

    def _mibig_extract_data_from_table(self):
        self.driver.implicitly_wait(3)
        table = self.driver.find_element(By.XPATH, self.query_data.TABLE)
        self.driver.implicitly_wait(3)
        table_text = table.text
        self._create_list_of_bgc_files(table_text)
        self._fill_dictionary(table_text)

    def _create_list_of_bgc_files(self, text):
        words = text.split()
        for word in words:
            if word.upper().startswith("BGC"):
                self.bgc_words.append(word)

    def _fill_dictionary(self, text):
        result = []
        temp_string = ""

        for line in text.split("\n"):
            if line.startswith("BGC"):
                if temp_string != "":
                    result.append(temp_string)
                temp_string = line
            else:
                temp_string += "\n" + line

        if temp_string != "":
            result.append(temp_string)

        for row in result:
            split_row = row.split('\n')
            cluster_id = split_row[0].split(' ')[0]
            self.output_dict[cluster_id] = dict()
            self.output_dict[cluster_id]['main_product'] = split_row[0].split(' ')[1]
            self.output_dict[cluster_id]['bionsythetic_class'] = split_row[1]
            self.output_dict[cluster_id]['organism'] = split_row[2]

    def get_bgc_list(self):
        return self.bgc_words

    def get_scraper_dict(self):
        return self.output_dict


if __name__ == "__main__":
    mibig_scraper = DataScraper(kingdom=KingdomNames.FUNGI, export_location=DirectoryType.LOCAL,
                                get_gene_data=False)
    bgc_list = mibig_scraper.get_bgc_list()
    scraper_dict = mibig_scraper.get_scraper_dict()
    ClusterExcelWriter(bgc_list=bgc_list, scraper_dict=scraper_dict).handle_data_from_directory(file_type=IODataTypes.GENBANK,
                                                                                                directory=DirectoryData.GENBANK_3_1)
