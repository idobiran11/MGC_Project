from dataclasses import dataclass


@dataclass
class MibigBGCs:
    PLANTS = ['BGC0000669', 'BGC0000670', 'BGC0000671', 'BGC0000672', 'BGC0000798', 'BGC0000810',
              'BGC0001313',
              'BGC0001314', 'BGC0001315', 'BGC0001316', 'BGC0001317', 'BGC0001318', 'BGC0001319',
              'BGC0001320',
              'BGC0001321', 'BGC0001322', 'BGC0001323', 'BGC0001324', 'BGC0001325', 'BGC0001756',
              'BGC0001799',
              'BGC0001997', 'BGC0002388', 'BGC0002389', 'BGC0002390', 'BGC0002391', 'BGC0002392',
              'BGC0002393',
              'BGC0002394', 'BGC0002395', 'BGC0002396', 'BGC0002397', 'BGC0002398', 'BGC0002399',
              'BGC0002400',
              'BGC0002401', 'BGC0002402', 'BGC0002403', 'BGC0002404', 'BGC0002405', 'BGC0002406',
              'BGC0002574',
              'BGC0002622', 'BGC0002721', 'BGC0002722', 'BGC0002723', 'BGC0002724']


@dataclass(frozen=True)
class KingdomNames:
    PLANT = "Viridiplantae"
    FUNGI = "Fungi"

@dataclass(frozen=True)
class DirectoryType:
    LOCAL: str = "local"
    CLUSTER: str = "cluster"


@dataclass(frozen=True)
class UrlData:
    MIBIG: str = "https://mibig.secondarymetabolites.org/query"


@dataclass(frozen=True)
class MibigQueryData:
    URL = "https://mibig.secondarymetabolites.org/query"
    QUERY_NAME = "/html[1]/body[1]/div[1]/div[1]/mibig-query[1]/div[1]/div[1]/div[1]/div[2]/mibig-query-builder[1]/div[1]/mibig-query-term[1]/div[1]/div[2]/input[1]"
    BUILD_QUERY = "/html[1]/body[1]/div[1]/div[1]/mibig-query[1]/div[1]/div[1]/ul[1]/li[2]/a[1]"
    DROP_DOWN = "/html[1]/body[1]/div[1]/div[1]/mibig-query[1]/div[1]/div[1]/div[1]/div[2]/mibig-query-builder[1]/div[1]/mibig-query-term[1]/div[1]/div[1]/select[1]"
    DD_KINGDOM = "Kingdom"
    FINAL_QUERY_BUTTON = "/html[1]/body[1]/div[1]/div[1]/mibig-query[1]/div[1]/div[1]/div[1]/div[2]/mibig-query-builder[1]/div[2]/div[2]/button[1]/i[1]"
    TABLE = "/html[1]/body[1]/div[1]/div[1]/mibig-query[1]/mibig-query-results[1]/div[3]/table[1]/tbody"


@dataclass(frozen=True)
class QueryDataNames:
    MIBIG: str = "mibig"
