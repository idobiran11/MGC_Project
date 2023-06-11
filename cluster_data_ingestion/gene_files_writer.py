import os
import pandas as pd
from Bio import SeqIO
from excel_write_config import DirectoryData, IODataTypes
from typing import Type
import json
import logging


class GeneCompoundFilesWriter:

    def __init__(self, directory_data: Type[DirectoryData] = DirectoryData, kingdom: str = "plants",
                 from_json: bool = True):
        self.from_json = from_json
        if kingdom == "plants":
            self.cluster_path = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.PLANT_CLUSTER_EXCEL}'
            self.write_directory = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.PLANT_GENE_DATA_DIR}'
            self.compound_write_directory = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.PLANT_COMPOUND_DATA_DIR}'
        elif kingdom == "fungi":
            self.cluster_path = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.FUNGI_CLUSTER_EXCEL}'
            self.write_directory = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.FUNGI_GENE_DATA_DIR}'
            self.compound_write_directory = f'{directory_data.GENERAL_DATA_DIR}/{directory_data.FUNGI_COMPOUND_DATA_DIR}'
        else:
            logging.error("Non Existent kingdom kwarg, write 'plants' or 'fungi'")
            raise Exception
        self.cluster_df = pd.read_excel(self.cluster_path)
        self.genbank_files = [directory_data.GENBANK_3_1, directory_data.GENBANK_3_0, directory_data.GENBANK_2_0]
        self.json_files = [directory_data.JSON_3_1, directory_data.JSON_3_0, directory_data.JSON_2_0,
                           directory_data.JSON_1_4]
        self._check_create_dir()

    def _check_create_dir(self):
        if not os.path.exists(self.write_directory):
            os.makedirs(self.write_directory)
            logging.info('created gene directory')

        if not os.path.exists(self.compound_write_directory):
            os.makedirs(self.compound_write_directory)
            logging.info('created compound directory')

    def _get_df_id_list(self):
        df = pd.read_excel(self.cluster_path)
        return df['mibig_id'].to_list()

    def _get_cluster_df_feature(self, cluster: str, feature: str):
        return self.cluster_df.loc[self.cluster_df['mibig_id'] == cluster, feature].values[0]

    def _iterate_and_create_files_from_gbk(self, cluster_list):
        i = 0
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
                        gene_row['absolute_start'] = self._get_cluster_df_feature(cluster=cluster_name,
                                                                                  feature='cluster_start') + gene_row[
                                                         'start']
                        gene_row['absolute_end'] = gene_row['absolute_start'] + (gene_row['end'] - gene_row['start'])
                        gene_row['gene'] = self.get_value(feature.qualifiers.get('gene'))
                        gene_row['product'] = self.get_value(feature.qualifiers.get('product'))
                        gene_row['transcript_id'] = self.get_value(feature.qualifiers.get('transcript_id'))
                        gene_row['db_xref'] = self.get_value(feature.qualifiers.get('db_xref'))
                        gene_row['protein_id'] = self.get_value(feature.qualifiers.get('protein_id'))
                        gene_row['gene_kind'] = self.get_value(feature.qualifiers.get('gene_kind'))
                        gene_row['note'] = self.get_value(feature.qualifiers.get('note'))
                        gene_row['mibig_version'] = directory.split('/')[-1]
                        df2 = pd.Series(gene_row).to_frame().transpose()
                        df = pd.concat([df, df2])
                    filepath = os.path.join(self.write_directory, f'{cluster_name}.xlsx')
                    df.reset_index(drop=True, inplace=True)
                    df.to_excel(filepath, index=True)
                logging.debug(f"Created {cluster_name} genbank file")
                i += 1
                break
        logging.info(f'Created {i} genbank files')

    def _iterate_and_add_data_from_json(self, cluster_list):
        i = 0
        for cluster_name in cluster_list:
            cluster_file_name = f'{cluster_name}.json'
            for directory in self.json_files:
                file_path = os.path.join(directory, cluster_file_name)
                if not os.path.exists(file_path):
                    logging.debug(f'{cluster_name} not in {directory}')
                    continue
                with open(file_path, 'r') as cluster_file:
                    json_data = json.load(cluster_file)
                    df = pd.DataFrame()
                    cluster_data = json_data.get('cluster')
                    if not cluster_data:
                        logging.debug(f'{cluster_name} has no cluster data in cluster file')
                        continue
                    gene_data = cluster_data.get('genes')
                    if not gene_data:
                        logging.debug(f'{cluster_name} has no gene data in cluster file')
                        continue
                    for gene_annotation in gene_data.get('annotations'):
                        gene_row = dict()
                        gene_row['protein_id'] = gene_annotation.get('id')
                        gene_row['gene'] = gene_annotation.get('name')
                        gene_row['product'] = gene_annotation.get('product')
                        gene_row['tailoring_function'] = gene_annotation.get('tailoring')
                        gene_row['mibig_version'] = directory.split('/')[-1]
                        gene_row['comments'] = gene_annotation.get('comments')
                        gene_function = gene_annotation.get('functions')
                        gene_row['function_category'] = None
                        gene_row['function_evidence'] = None
                        if gene_function:
                            gene_row['function_category'] = gene_function[0].get('category')
                            gene_row['function_evidence'] = gene_function[0].get('evidence')
                        gene_row['extra_gene_id'] = None
                        gene_row['location'] = None
                        try:
                            another_function = gene_function[1]
                            logging.warning(
                                f'{cluster_name} in gene {gene_row["gene"]} has multiple gene functions: {another_function}')
                        except:
                            None
                        df2 = pd.Series(gene_row).to_frame().transpose()
                        df = pd.concat([df, df2])
                    extra_genes = gene_data.get('extra_genes')
                    if extra_genes:
                        for extra_gene in extra_genes:
                            gene_row = dict()
                            gene_row['protein_id'] = None
                            gene_row['gene'] = None
                            gene_row['product'] = None
                            gene_row['tailoring_function'] = None
                            gene_row['mibig_version'] = directory.split('/')[-1]
                            gene_row['comments'] = None
                            gene_row['function_category'] = None
                            gene_row['function_evidence'] = None
                            gene_row['extra_gene_id'] = extra_gene.get('id')
                            gene_row['extra_gene_location'] = extra_gene.get('location')
                            df2 = pd.Series(gene_row).to_frame().transpose()
                            df = pd.concat([df, df2])

                    filepath = os.path.join(self.write_directory, f'json_{cluster_name}.xlsx')
                    df.reset_index(drop=True, inplace=True)
                    df.to_excel(filepath, index=True)
                    i += 1
                    logging.debug(f"Created {cluster_name} json file")
                    break
        logging.info(f'Created {i} json files')

    def _create_compound_files(self, cluster_list):
        i = 0
        for cluster_name in cluster_list:
            cluster_file_name = f'{cluster_name}.json'
            for directory in self.json_files:
                file_path = os.path.join(directory, cluster_file_name)
                if not os.path.exists(file_path):
                    logging.debug(f'{cluster_name} not in {directory}')
                    continue
                with open(file_path, 'r') as cluster_file:
                    json_data = json.load(cluster_file)
                    df = pd.DataFrame()
                    cluster_data = json_data.get('cluster')
                    if not cluster_data:
                        logging.debug(f'{cluster_name} has no cluster data in cluster file of version {directory}')
                        continue
                    compounds = cluster_data.get('compounds')
                    if not compounds:
                        logging.warning(f'{cluster_name} has no compounds')
                        continue
                    for compound in compounds:
                        gene_row = dict()
                        gene_row['compound'] = compound.get('compound')
                        gene_row['database_id'] = compound.get('database_id')
                        gene_row['mol_mass'] = compound.get('mol_mass')
                        gene_row['molecular_formula'] = compound.get('molecular_formula')
                        gene_row['mibig_version'] = directory.split('/')[-1]
                        df2 = pd.Series(gene_row).to_frame().transpose()
                        df = pd.concat([df, df2])
                    filepath = os.path.join(self.compound_write_directory, f'{cluster_name}.xlsx')
                    df.reset_index(drop=True, inplace=True)
                    df.to_excel(filepath, index=True)
                    logging.debug(f"Created {cluster_name} compounds file")
                    i += 1
                    break
        logging.info(f'Created {i} compounds files')

    @staticmethod
    def get_value(lst, index=0):
        try:
            return lst[index]
        except Exception as e:
            return None

            # Placeholder for iterateing over genes- set stop point and run from here

    def write_gene_and_compounds_files(self):
        cluster_list = self._get_df_id_list()
        self._iterate_and_create_files_from_gbk(cluster_list)
        self._iterate_and_add_data_from_json(cluster_list)
        self._create_compound_files(cluster_list)


if __name__ == "__main__":
    GeneCompoundFilesWriter(directory_data=DirectoryData).write_gene_and_compounds_files()
