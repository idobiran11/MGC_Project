import os

import pandas as pd
from Bio import SeqIO
from MGC_Project.cluster_data_ingestion.excel_write_config import IODataTypes, DirectoryData, DataframeColumns


class ExcelWriter:

    def __init__(self, bgc_list: list, scraper_dict: dict, output_directory: str = DirectoryData.GENERAL_DATA_DIR,
                 excel_name: str = DirectoryData.CLUSTER_EXCEL, excel_columns: list = DataframeColumns.CLUSTER,
                 write_gene_data: bool = False, ):
        self.bgc_list = bgc_list
        self.output_directory = output_directory
        self.excel_name = excel_name
        self.df = pd.DataFrame(columns=excel_columns)
        self.write_gene_data = write_gene_data
        self.scraper_dict = scraper_dict

    def _write_to_cluster_df(self, seq_record):
        cluster_scraped_dict = self.scraper_dict[seq_record.id]
        value_dict = {'mibig_id': seq_record.id,
                      'cluster_doi': 'None',
                      'cluster_name': 'None',
                      'organism': cluster_scraped_dict['organism'],
                      'cluster_start': int(seq_record.annotations['structured_comment']['antiSMASH-Data']['Orig. start']),
                      'cluster_end': int(seq_record.annotations['structured_comment']['antiSMASH-Data']['Orig. end']),
                      'cluster_genbank_link': 'None',
                      'num_of_genes': self._find_num_of_genes(seq_record),
                      'bionsythetic_class': cluster_scraped_dict['bionsythetic_class'],
                      'description': seq_record.description,
                      'main_product': cluster_scraped_dict['main_product']}
        # 'organism': seq_record.annotations['organism']
        df2 = pd.Series(value_dict).to_frame().transpose()
        self.df = pd.concat([self.df, df2])

    def _write_output_excel(self):
        directory = self.output_directory
        suffix = self.excel_name
        filepath = os.path.join(directory, suffix)
        self.df.to_excel(filepath, index=True)

    @staticmethod
    def _find_num_of_genes(seq_record):
        num_genes = 0
        feature_list = seq_record.features
        for feature in feature_list:
            if feature.type != 'gene':
                continue
            num_genes += 1
        return num_genes

    def handle_data_from_directory(self, directory: str, file_type: str):
        dir_list = os.listdir(directory)

        if file_type == IODataTypes.GENBANK:
            for file_name in dir_list:
                cluster, suffix = file_name.split('.')
                if not cluster in self.bgc_list:
                    continue
                path = f"{directory}/{file_name}"
                for seq_record in SeqIO.parse(path, file_type):
                    if self.excel_name == DirectoryData.CLUSTER_EXCEL:
                        self._write_to_cluster_df(seq_record)
                    if self.write_gene_data:
                        None
            self._write_output_excel()



        # elif file_type == IODataTypes.JSON:
        #     for file_name in dir_list:
        #         path = f"{directory}/{file_name}"
        #         json_file = open(path)
        #         json_data = json.load(json_file)
        #         x = 4
