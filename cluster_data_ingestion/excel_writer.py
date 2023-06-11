import os
import pandas as pd
from Bio import SeqIO
from cluster_data_ingestion.excel_write_config import IODataTypes, DirectoryData
import json
import logging


class ClusterExcelWriter:

    def __init__(self, bgc_list: list, scraper_dict: dict, output_directory: str = DirectoryData.GENERAL_DATA_DIR,
                 excel_name: str = DirectoryData.CLUSTER_EXCEL,
                 write_gene_data: bool = False, ):
        self.bgc_list = bgc_list
        self.output_directory = output_directory
        self.excel_name = excel_name
        self.df = pd.DataFrame()
        self.write_gene_data = write_gene_data
        self.scraper_dict = scraper_dict

    def _check_create_dir(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    @staticmethod
    def _extract_publications_from_json(json_file):
        json_cluster = json_file.get('cluster')
        if json_cluster:
            publications = json_cluster.get('publications')
            return publications
        return None

    @staticmethod
    def _extract_start_end_completeness_from_json(json_file):
        json_cluster = json_file.get('cluster')
        if json_cluster:
            loci = json_cluster.get('loci')
            if loci:
                completeness = loci.get('completeness')
                start = loci.get('start_coord')
                end = loci.get('end_coord')
                evidence = loci.get('evidence')
                acccession = loci.get('accession')
                return [completeness, start, end, evidence, acccession]
        return None

    def _write_to_cluster_df(self, seq_record, mibig_version, json_path):
        with open(json_path, 'r') as file:
            json_record = json.load(file)
        cluster_scraped_dict = self.scraper_dict[seq_record.id]
        completeness, start, end, evidence, accession = self._extract_start_end_completeness_from_json(json_record)
        notes = []
        if not start:
            start = int(seq_record.annotations['structured_comment']['antiSMASH-Data']['Orig. start'])
            notes.append('start calculated from gbk')
        if not end:
            end = int(seq_record.annotations['structured_comment']['antiSMASH-Data']['Orig. end'])
            notes.append('end calculated from gbk')
        value_dict = {'mibig_id': seq_record.id,
                      'accession': accession,
                      'organism': cluster_scraped_dict['organism'],
                      'cluster_start': start,
                      'cluster_end': end,
                      'num_of_coding_sequences': self._find_num_of_genes(seq_record),
                      'bionsythetic_class': cluster_scraped_dict['bionsythetic_class'],
                      'description': seq_record.description,
                      'main_product': cluster_scraped_dict['main_product'],
                      'mibig_version': mibig_version,
                      'completeness': completeness,
                      'evidence': evidence,
                      'publications': self._extract_publications_from_json(json_record),
                      'ido_notes': notes}
        # 'organism': seq_record.annotations['organism']
        df2 = pd.Series(value_dict).to_frame().transpose()
        self.df = pd.concat([self.df, df2])

    def _write_output_excel(self):
        directory = self.output_directory
        suffix = self.excel_name
        filepath = os.path.join(directory, suffix)
        self.df.reset_index(drop=True, inplace=True)
        self.df.to_excel(filepath, index=True)

    @staticmethod
    def _find_num_of_genes(seq_record):
        num_genes = 0
        feature_list = seq_record.features
        for feature in feature_list:
            if feature.type != 'CDS':
                continue
            num_genes += 1
        return num_genes

    def _find_json_path(self, bgc_name):
        directories = [DirectoryData.JSON_3_1, DirectoryData.JSON_3_0, DirectoryData.JSON_2_0]
        file_name = f'{bgc_name}.json'
        for dir in directories:
            file_path = f"{dir}/{file_name}"
            if os.path.exists(file_path):
                logging.debug(f'Json of {bgc_name} found in {dir}')
                return file_path
        logging.warning(f"No Json File found for {bgc_name}, returning None")
        return None

    def handle_data_from_directory(self, file_type: str):
        directories = [DirectoryData.GENBANK_3_1, DirectoryData.GENBANK_3_0, DirectoryData.GENBANK_2_0]
        if file_type == IODataTypes.GENBANK:
            i = 0
            for bgc in self.bgc_list:
                file_name = f'{bgc}.gbk'
                for directory in directories:
                    path = f"{directory}/{file_name}"
                    if not os.path.exists(path):
                        if directory == DirectoryData.GENBANK_2_0:
                            logging.warning(f'{file_name} not in data')
                        continue
                    for seq_record in SeqIO.parse(path, file_type):
                        mibig_version = directory.split('/')[-1]
                        json_path = self._find_json_path(bgc)
                        self._write_to_cluster_df(seq_record, mibig_version, json_path=json_path)
                        i += 1
                        logging.debug(f'{i} clusters added, {bgc} found in {directory}')
                    break
            logging.info(f'Added {i} clusters to main cluster file')
            self._write_output_excel()

        # elif file_type == IODataTypes.JSON:
        #     for file_name in dir_list:
        #         path = f"{directory}/{file_name}"
        #         json_file = open(path)
        #         json_data = json.load(json_file)
        #         x = 4
