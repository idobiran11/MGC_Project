import os
import pandas as pd
from Bio import SeqIO
from excel_write_config import DirectoryData, IODataTypes
from typing import Type
from dataclasses import dataclass

class GeneFilesWriter:

    def __init__(self, directory_data: DirectoryData):
        self.cluster_path = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.PLANT_CLUSTER_EXCEL}'
        self.genbank_files = directory_data.GENBANK_3_1
        self.write_directory = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.GENE_DATA_DIR}'

    def _get_df_id_list(self):
        df = pd.read_excel(self.cluster_path)
        return df['mibig_id'].to_list()

    def _iterate_and_create_files(self, cluster_list):
        for cluster_name in cluster_list:
            cluster_file_name = f'{cluster_name}.gbk'
            file_path = os.path.join(self.genbank_files, cluster_file_name)
            for seq_record in SeqIO.parse(file_path, IODataTypes.GENBANK):
                x = 3
                # Placeholder for iterateing over genes- set stop point and run from here

    def write_gene_files(self):
        cluster_list = self._get_df_id_list()
        self._iterate_and_create_files(cluster_list)


if __name__ == "__main__":
    GeneFilesWriter(directory_data=DirectoryData).write_gene_files()
