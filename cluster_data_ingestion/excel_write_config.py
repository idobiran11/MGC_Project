from dataclasses import dataclass


@dataclass(frozen=True)
class DirectoryData:
    JSON_3_1: str = "cluster_data_ingestion/data/mibig/json/mibig_json_3.1"
    GENBANK_3_1: str = "cluster_data_ingestion/data/mibig/genbank/mibig_gbk_3.1"
    GENERAL_DATA_DIR = "general_data"
    CLUSTER_EXCEL = "mgc_clusters.xlsx"


@dataclass(frozen=True)
class IODataTypes:
    GENBANK: str = "genbank"
    JSON: str = "json"


@dataclass(frozen=True)
class DataframeColumns:
    CLUSTER = ['mibig_id', 'cluster_doi', 'cluster_name', 'organism', 'cluster_start', 'cluster_end',
               'cluster_genbank_link', 'num_of_genes', 'bionsythetic_class', 'description', 'main_product']
