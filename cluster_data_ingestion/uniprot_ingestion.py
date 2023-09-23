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
                f"../{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}/{self.cluster_id}.xlsx")
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

    def write_cross_references_files(self):
        for result in self.uniprot_results:
            cross_references_list = result.get("uniProtKBCrossReferences")
            database = []
            id = []
            entry_type = result.get('entryType')
            for reference in cross_references_list:
                database.append(reference.get('database'))
                id.append(reference.get('id'))
            df = pd.DataFrame({'database': database, 'id': id})
            output_directory = f'../{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}/{DirectoryData.UNIPROT_CROSS_REFERENCES}/{self.cluster_id}_uniprot_crossreference'
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            output_path = f'{output_directory}/{self.gene_id}_{entry_type}.xlsx'
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

    def get_entry(self):
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


def uniprot_handler(
        plant_gene_data_path: str = f'../{DirectoryData.GENERAL_DATA_DIR}/{DirectoryData.PLANT_GENE_DATA_DIR}'):
    file_paths = glob.glob(os.path.join(plant_gene_data_path, 'BGC*'))

    # Iterate over the list of file paths
    for file_path in file_paths:
        # Extract the file name (without the directory path)
        file_name = os.path.basename(file_path)

        # Split the file name based on the period ('.')
        parts = file_name.split('.')
        cluster_name = parts[0]
        genes_in_cluster = UniProtClustertoGene(cluster_name).get_genes_in_cluster()
        if genes_in_cluster:
            for gene in genes_in_cluster:
                ingestion = UniProtApiIngestion(gene_id=gene, cluster_id=cluster_name)
                ingestion.write_cross_references_files()
    logger.info("Finished Writing gene files crossreferences Successfully!")



if __name__ == "__main__":
    uniprot_handler()