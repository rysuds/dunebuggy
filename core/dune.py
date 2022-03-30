from httpx import Client
from models.constants import (
    DEFAULT_HEADERS,
    LOGIN_URL,
    CSRF_URL,
    BASE_URL,
    API_AUTH_URL,
    SESSION_URL,
    GRAPH_QL_URL,
    FIND_QUERY,
    GET_RESULT_QUERY,
    FIND_RESULT_DATA_BY_RESULT_QUERY
)
from models.query import Query, QueryMetadata, QueryResultData
from core.dunequery import DuneQuery


class Dune:
    def __init__(self, username=None, password=None):
        self.client = Client()
        self.client.headers.update(DEFAULT_HEADERS)
        if username is not None and password is not None:
            self.logged_in = self.login(username, password)
        else:
            self.logged_in = False

    def login(self, username: str, password: str) -> bool:
        self.client.get(LOGIN_URL)
        self.client.post(CSRF_URL)
        csrf_token = self.client.cookies.get('csrf')

        form_data = {
            'action': 'login',
            'username': username,
            'password': password,
            'csrf': csrf_token,
            'next': BASE_URL
        }
        self.client.post(API_AUTH_URL, data=form_data)

        # Fetch AUTH token
        response = self.client.post(SESSION_URL)
        if response.status_code >= 400:
            print("Dune Login Failed: Defaulting to No User/Pass")
            return False

        token = response.json().get('token')
        self.client.headers.update(
            {'authorization': f'Bearer {token}'}
        )
        return True

    def _post_graph_ql(self, operation: str, query: str, variables: dict) -> dict:
        data = {
            "operationName": operation,
            "query": query,
            "variables": variables
        }
        response = self.client.post(GRAPH_QL_URL, json=data)
        return response.json()

    def _fetch_query_metadata(self, query_id: int) -> QueryMetadata:
        raw_metadata = self._post_graph_ql(
            "FindQuery",
            FIND_QUERY,
            {"id": query_id}
        )
        metadata = raw_metadata['data']['queries'][0]
        return QueryMetadata(**metadata)

    def _fetch_result_id(self, query_id: int) -> str:
        result_id_data = self._post_graph_ql(
            "GetResult",
            GET_RESULT_QUERY,
            {"query_id": query_id}
        )
        return result_id_data\
            .get('data')\
            .get('get_result')\
            .get('result_id')

    def _fetch_result_data(self, query_id: int) -> QueryResultData:
        result_id = self._fetch_result_id(query_id)
        raw_result = self._post_graph_ql(
            "FindResultDataByResult",
            FIND_RESULT_DATA_BY_RESULT_QUERY,
            {"result_id": result_id}
        )

        query_result_data = raw_result['data']['query_results'][0]
        query_result_data['raw_data'] = raw_result['data']['get_result_by_result_id']
        return QueryResultData(**query_result_data)

    # Should return a DuneQuery Object, that can be used to grab the table, charts etc
    # Streaming Responses??
    def fetch_query(self, query_id: int) -> DuneQuery:
        metadata = self._fetch_query_metadata(query_id)
        result_data = self._fetch_result_data(query_id)
        query = Query(metadata=metadata, result_data=result_data)
        return DuneQuery(query)
