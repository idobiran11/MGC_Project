import requests
import logging
from dataclasses import dataclass

logging.basicConfig(format=' %(asctime)s | %(levelname)s | %(message)s', level=logging.INFO)
logger = logging.getLogger('uniprot')


@dataclass(frozen=True)
class GeneDBNames:
    GO: str = "GO"
    KEGG: str = "KEGG"
    PANTHER: str = "PANTHER"


class UniProtApiIngestion:

    def __init__(self, gene_id: str):
        self.gene_id = gene_id
        self.uniport_json_response = self._get_uniprot_request()
        self.uniprot_results = self._get_uniprot_results()
        self.annotation_dict = self._get_annotation_dict()

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
        return results[0]

    def _get_annotation_dict(self, go: bool = True, kegg: bool = True, panther: bool = True):

        database_list = []
        if go:
            database_list.append(GeneDBNames.GO)
        if kegg:
            database_list.append(GeneDBNames.KEGG)
        if panther:
            database_list.append(GeneDBNames.PANTHER)
        results = self.uniprot_results
        cross_reference = results.get('uniProtKBCrossReferences')
        annotation_dictionary = dict()
        for reference in cross_reference:
            ref_db = reference.get('database')
            if ref_db in database_list:
                annotation_dictionary[ref_db] = annotation_dictionary.get(ref_db, [])
                annotation_dictionary[ref_db].append(reference)
        return annotation_dictionary

    def get_go_annotation_for_df(self):
        go_dict = self.annotation_dict.get(GeneDBNames.GO)



if __name__ == "__main__":
    ingestion = UniProtApiIngestion(gene_id='CYP705A12')
    annotation_dict = ingestion.get_annotation_dict()
    x = 3
