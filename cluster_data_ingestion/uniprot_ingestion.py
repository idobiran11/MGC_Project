import requests
import logging
import os
import glob
import json
import pandas as pd
import numpy as np
from Bio.KEGG.REST import kegg_find, kegg_get
from dataclasses import dataclass
from cluster_data_ingestion.excel_write_config import DirectoryData

CURRENT_FILE_PATH = os.path.abspath(__file__)
ROOT_DIR_PATH = os.path.dirname(os.path.dirname(CURRENT_FILE_PATH))

logging.basicConfig(format=' %(asctime)s | %(levelname)s | %(message)s', level=logging.INFO)
logger = logging.getLogger('uniprot')


@dataclass(frozen=True)
class GeneDBNames:
    GO: str = "GO"
    KEGG: str = "KEGG"
    PANTHER: str = "PANTHER"


class UniProtClustertoGene:
    def __init__(self, cluster_id: str):
        self.cluster_id = cluster_id
        self.cluster_file = self._read_cluster_gene_file()

    def _read_cluster_gene_file(self):
        try:
            df = pd.read_excel(
                f"{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}/{self.cluster_id}.xlsx")
            return df
        except Exception as e:
            logger.error(f"Failed reading cluster file on cluster: {self.cluster_id} with error: {e}")

    def get_genes_in_cluster(self):
        df = self.cluster_file
        df = df[df['gene'].notnull()]
        # df['search_genes'] = df['gene'].str.split(':').str[1]
        if not df.empty:
            return df['gene'].unique().tolist()


class UniProtApiIngestion:

    def __init__(self, gene_id: str, cluster_id: str):
        self.gene_id = gene_id
        self.cluster_id = cluster_id
        self.uniport_json_response = self._get_uniprot_request()
        self.uniprot_results = self._get_uniprot_results()
        self.annotation_dict = self.get_annotation_dict()
        pass

    def _get_uniprot_request(self):
        uniprot_url = f"https://rest.uniprot.org/uniprotkb/search?query=(gene:{self.gene_id})"
        response = requests.get(uniprot_url)
        json_response = response.json()
        return json_response

    def _get_uniprot_results(self):
        results = self.uniport_json_response.get('results')
        results_len = len(results)
        if results_len > 1:
            logger.warning(f"Length of uniport results for gene {self.gene_id} is {results_len}")
        return results

    def write_cross_references_files(self, output_directory: str):
        for result in self.uniprot_results:
            cross_references_list = result.get("uniProtKBCrossReferences")
            database = []
            id = []
            entry_type = result.get('entryType')
            for reference in cross_references_list:
                database.append(reference.get('database'))
                id.append(reference.get('id'))
            df = pd.DataFrame({'database': database, 'id': id})
            file_name = f'{self.gene_id}_{entry_type}.xlsx'
            output_path = f'{output_directory}/{file_name}'
            df.to_excel(output_path)

    def get_annotation_dict(self, go: bool = False, kegg: bool = False, panther: bool = False):

        database_list = []
        if go:
            database_list.append(GeneDBNames.GO)
        if kegg:
            database_list.append(GeneDBNames.KEGG)
        if panther:
            database_list.append(GeneDBNames.PANTHER)
        results = self.uniprot_results
        for result in results:
            cross_reference = result.get('uniProtKBCrossReferences')
            annotation_dictionary = dict()
            for reference in cross_reference:
                ref_db = reference.get('database')
                if ref_db in database_list:
                    annotation_dictionary[ref_db] = annotation_dictionary.get(ref_db, [])
                    annotation_dictionary[ref_db].append(reference)
            return annotation_dictionary

    def get_go_annotation_for_df(self):
        go_df_dict = self.annotation_dict.get(GeneDBNames.GO)
        return go_df_dict


class KEGGIngestion:
    def __init__(self, id):
        self.id = id

    def get_kegg_entry(self):
        # return kegg_get(self.id, "aaseq")
        kegg_url = f"https://rest.kegg.jp/get/{self.id}"
        response = requests.get(kegg_url)
        kegg_output = response.text
        results = {}
        for line in kegg_output.split('\n'):
            splits = line.split()
            if not line.startswith(' '):
                if len(splits) > 0:
                    key = splits[0]
                    value = ' '.join(splits[1:])
                    results[key] = value
            else:
                results[key] += ' '.join(splits)
        return pd.DataFrame(results, index=[self.id])


class CrossReferenceIterator:
    def __init__(self,
                 plant_gene_data_path: str = f'{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}',
                 crossreference_directory: str = f"{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}/{DirectoryData.UNIPROT_CROSS_REFERENCES}",
                 output_directory=f"{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}"):
        self.plant_gene_data_path = plant_gene_data_path
        self.crossreference_directories = glob.glob(os.path.join(crossreference_directory, 'BGC*'))
        self.output_directory = output_directory

    def write_cross_reference_data(self):
        file_paths = glob.glob(os.path.join(self.plant_gene_data_path, 'BGC*'))

        # Iterate over the list of file paths
        for file_path in file_paths:
            # Extract the file name (without the directory path)
            file_name = os.path.basename(file_path)

            # Split the file name based on the period ('.')
            parts = file_name.split('.')
            cluster_name = parts[0]
            output_directory = f'{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}/{DirectoryData.UNIPROT_CROSS_REFERENCES}/{cluster_name}_uniprot_crossreference'
            if os.path.exists(output_directory):
                logger.warning(f"Exists Directory {output_directory}, skipping creation")
            else:
                os.makedirs(output_directory)
                genes_in_cluster = UniProtClustertoGene(cluster_name).get_genes_in_cluster()
                if genes_in_cluster:
                    for gene in genes_in_cluster:
                        ingestion = UniProtApiIngestion(gene_id=gene, cluster_id=cluster_name)
                        ingestion.write_cross_references_files(output_directory)
            logger.info(f"Finished Writing gene files crossreferences for file path {file_paths} Successfully!")

    def get_kegg_data(self):
        kegg_final_df = pd.DataFrame()
        for dir in self.crossreference_directories:
            ref_files = glob.glob(os.path.join(dir, '*.xlsx'))
            if len(ref_files) == 0:
                logger.info(
                    f"Directory {dir} has no crossreference files, probably uses hypothetical genes in gene files")
            else:
                cluster_ref = ref_files[0].split('/')[-2].split('_')
                cluster_name = cluster_ref[0]
                files_with_kegg = {}
                for file in ref_files:

                    df = pd.read_excel(file)
                    kegg_files = (find_kegg_ids(df))
                    if not kegg_files:
                        continue
                    file_type = file.split('/')[-1].split('.')[0]
                    if file_type not in files_with_kegg:
                        files_with_kegg[file_type] = kegg_files
                    else:
                        files_with_kegg[file_type].extend(kegg_files)
                for file_type, value in files_with_kegg.items():
                    for id in files_with_kegg[file_type]:
                        kegg_df = KEGGIngestion(id).get_kegg_entry()
                        kegg_df.insert(0, 'cluster_name', cluster_name)
                        kegg_df.insert(1, 'reference_name', file_type)
                        kegg_final_df = pd.concat([kegg_final_df, kegg_df])
        logger.info("Succesfully Created KEGG dataframe")
        return kegg_final_df


def uniprot_plant_handler(
        plant_gene_data_path: str = f'{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}',
        crossreference_directory: str = f"{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}/{DirectoryData.UNIPROT_CROSS_REFERENCES}",
        output_directory=f"{ROOT_DIR_PATH}/{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}"):
    cross_ref_iterator = CrossReferenceIterator(plant_gene_data_path, crossreference_directory, output_directory)
    cross_ref_iterator.write_cross_reference_data()
    kegg_df = cross_ref_iterator.get_kegg_data()
    kegg_dir = f"{output_directory}/{DirectoryData.KEGG_DATA}"
    if not os.path.exists(kegg_dir):
        logger.info(f"{kegg_dir} doesnt exist. Creating.")
        os.makedirs(kegg_dir)
    kegg_df.to_excel(f"{kegg_dir}/KEGG_data.xlsx")
    x=4


def find_kegg_ids(df: pd.DataFrame) -> list:
    df = df[df['database'] == "KEGG"]
    if not df.empty:
        return df["id"].to_list()
    else:
        return None


if __name__ == "__main__":
    uniprot_plant_handler()
