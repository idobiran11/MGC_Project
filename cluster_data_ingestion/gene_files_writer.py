import os
import pandas as pd
from Bio import SeqIO
from excel_write_config import DirectoryData, IODataTypes
from typing import Type


class GeneFilesWriter:

    def __init__(self, directory_data: Type[DirectoryData]=DirectoryData, kingdom: str = "plants"):
        if kingdom == "plants":
            self.cluster_path = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.PLANT_CLUSTER_EXCEL}'
            self.write_directory = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.PLANT_GENE_DATA_DIR}'
        elif kingdom == "fungi":
            self.cluster_path = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.FUNGI_CLUSTER_EXCEL}'
            self.write_directory = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.FUNGI_GENE_DATA_DIR}'
        else:
            print("Non Existent kingdom kwarg, write 'plants' or 'fungi'")
            raise Exception
        self.genbank_files = [directory_data.GENBANK_3_1, directory_data.GENBANK_3_0, directory_data.GENBANK_2_0]
        self._check_create_dir()

    def _check_create_dir(self):
        if not os.path.exists(self.write_directory):
            os.makedirs(self.write_directory)

    def _get_df_id_list(self):
        df = pd.read_excel(self.cluster_path)
        return df['mibig_id'].to_list()

    def _iterate_and_create_files(self, cluster_list):
        for cluster_name in cluster_list:
            cluster_file_name = f'{cluster_name}.gbk'
            for directory in self.genbank_files:
                file_path = os.path.join(directory, cluster_file_name)
                if not os.path.exists(file_path):
                    continue
                for seq_record in SeqIO.parse(file_path, IODataTypes.GENBANK):
                    features = seq_record.features
                    df = pd.DataFrame()
                    for feature in features:
                        gene_row = dict()
                        gene_row['feature_type'] = feature.type
                        gene_row['start'] = feature.location.start
                        gene_row['end'] = feature.location.end
                        gene_row['gene'] = self.get_value(feature.qualifiers.get('gene'))
                        gene_row['product'] = self.get_value(feature.qualifiers.get('product'))
                        gene_row['transcript_id'] = self.get_value(feature.qualifiers.get('transcript_id'))
                        gene_row['db_xref'] = self.get_value(feature.qualifiers.get('db_xref'))
                        gene_row['protein_id'] = self.get_value(feature.qualifiers.get('protein_id'))
                        gene_row['gene_kind'] = self.get_value(feature.qualifiers.get('gene_kind'))
                        gene_row['note'] = self.get_value(feature.qualifiers.get('note'))
                        df2 = pd.Series(gene_row).to_frame().transpose()
                        df = pd.concat([df, df2])
                    filepath = os.path.join(self.write_directory, f'{cluster_name}.xlsx')
                    df.reset_index(drop=True, inplace=True)
                    df.to_excel(filepath, index=True)
                print(f"Created {cluster_name} genbank file")
                break

    @staticmethod
    def get_value(lst, index=0):
        try:
            return lst[index]
        except Exception as e:
            return None

            # Placeholder for iterateing over genes- set stop point and run from here

    def write_gene_files(self):
        cluster_list = self._get_df_id_list()
        self._iterate_and_create_files(cluster_list)


if __name__ == "__main__":
    GeneFilesWriter(directory_data=DirectoryData).write_gene_files()
