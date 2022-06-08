from enum import Enum

BASE_URL = "https://dune.com"
LOGIN_URL = f"{BASE_URL}/auth/login"
API_URL = f"{BASE_URL}/api"
API_AUTH_URL = f"{API_URL}/auth"
SESSION_URL = f"{API_AUTH_URL}/session"
CSRF_URL = f"{API_AUTH_URL}/csrf"
GRAPH_QL_URL = "https://core-hsr.duneanalytics.com/v1/graphql"

DEFAULT_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
              'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'dnt': '1',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'origin': BASE_URL,
    'upgrade-insecure-requests': '1',
    'x-hasura-api-key': ''
}


class DatasetId(int, Enum):
    ETHEREUM = 4
    XDAI = 6
    POLYGON = 7
    OPTIMISM_1 = 8
    OPTIMISM_2 = 10
    BINANCE = 9
    SOLANA = 1


class ParameterEnum(str, Enum):
    TEXT = 'text'
    ENUM = 'enum'
    DATETIME = 'datetime'
