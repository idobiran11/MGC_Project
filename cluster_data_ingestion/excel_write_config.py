from dataclasses import dataclass


@dataclass(frozen=True)
class DirectoryData:
    JSON_3_1: str = "cluster_data_ingestion/data/mibig/json/mibig_json_3.1"
    JSON_3_0: str = "cluster_data_ingestion/data/mibig/json/mibig_json_3.0"
    JSON_2_0: str = "cluster_data_ingestion/data/mibig/json/mibig_json_2.0"
    JSON_1_4: str = "cluster_data_ingestion/data/mibig/json/mibig_json_1.4"
    GENBANK_3_1: str = "cluster_data_ingestion/data/mibig/genbank/mibig_gbk_3.1"
    GENBANK_3_0: str = "cluster_data_ingestion/data/mibig/genbank/mibig_gbk_3.0"
    GENBANK_2_0: str = "cluster_data_ingestion/data/mibig/genbank/mibig_gbk_2.0"
    GENERAL_DATA_DIR = "general_data"
    CLUSTER_EXCEL = "mgc_clusters.xlsx"
    PLANT_CLUSTER_EXCEL = "mgc_plant_clusters.xlsx"
    FUNGI_CLUSTER_EXCEL = "mgc_fungi_clusters.xlsx"
    GENE_DATA_DIR = "gene_data"
    PLANT_GENE_DATA_DIR = "plant_gene_data"
    FUNGI_GENE_DATA_DIR = "fungi_gene_data"
    PLANT_COMPOUND_DATA_DIR = "plant_compound_data"
    FUNGI_COMPOUND_DATA_DIR = "fungi_compound_data"
    UNIPROT_CROSS_REFERENCES = "uniprot_crossreferences"
    KEGG_DATA = "KEGG_data"


@dataclass(frozen=True)
class IODataTypes:
    GENBANK: str = "genbank"
    JSON: str = "json"
