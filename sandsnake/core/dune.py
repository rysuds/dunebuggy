from uuid import UUID
from httpx import Client
from random import randint
from typing import List, Optional
from sandsnake.models.constants import (
    DEFAULT_HEADERS,
    LOGIN_URL,
    CSRF_URL,
    BASE_URL,
    API_AUTH_URL,
    SESSION_URL,
    GRAPH_QL_URL,
    FIND_QUERY,
    GET_RESULT_QUERY,
    FIND_RESULT_DATA_BY_RESULT_QUERY,
    UPSERT_QUERY,
    EXECUTE_QUERY,
    FIND_SESSION_USER,
    FIND_RESULT_DATA_BY_JOB
)
from sandsnake.models.query import (
    Query, QueryMetadata,
    QueryResultData, QueryParameter,
    Dataset
)
from sandsnake.core.dunequery import DuneQuery
from sandsnake.core.exceptions import DuneError


class Dune:
    def __init__(self, username=None, password=None):
        self.client = Client()
        self.client.headers.update(DEFAULT_HEADERS)
        self.access_token = None
        self.token = None
        self.sub = None
        self.user_id = None

        if username is not None and password is not None:
            self.login(username, password)

    def _post_graph_ql(self, operation: str, query: str, variables: dict) -> dict:
        data = {
            "operationName": operation,
            "query": query,
            "variables": variables
        }
        response = self.client.post(GRAPH_QL_URL, json=data)
        return response.json()

    def _get_user_id(self, sub: UUID) -> int:
        user_info = self._post_graph_ql(
            "FindSessionUser",
            FIND_SESSION_USER,
            {"sub": sub}
        )
        return user_info["data"]["users"][0]["id"]

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

        self.token = response.json().get('token')
        self.access_token = response.json().get('accessToken')
        self.sub = response.json().get('sub')

        self.client.headers.update(
            {'authorization': f'Bearer {self.token}'}
        )
        self.user_id = self._get_user_id(self.sub)
        return True

    def _fetch_query_metadata(self, query_id: int) -> QueryMetadata:
        raw_metadata = self._post_graph_ql(
            "FindQuery",
            FIND_QUERY,
            {"id": query_id}
        )
        metadata = raw_metadata['data']['queries'][0]
        return QueryMetadata(**metadata)

    def _fetch_result_id(self, query_id: int, parameters: Optional[List[QueryParameter]] = None) -> str:
        variables = {"query_id": query_id}
        if parameters is not None:
            parameters = [
                param.dict() for param in parameters if type(param) == QueryParameter]
            variables['parameters'] = parameters
        result_id_data = self._post_graph_ql(
            "GetResult",
            GET_RESULT_QUERY,
            variables
        )
        result = result_id_data.get('data').get('get_result')
        return result.get('result_id'), result.get('job_id')

    def _fetch_result_data_by_job(self, job_id: UUID) -> QueryResultData:
        raw_result = self._post_graph_ql(
            "FindResultDataByJob",
            FIND_RESULT_DATA_BY_JOB,
            {"job_id": job_id}
        )
        return self._process_result_data(raw_result)

    def _fetch_result_data_by_result(self, result_id: int) -> QueryResultData:
        raw_result = self._post_graph_ql(
            "FindResultDataByResult",
            FIND_RESULT_DATA_BY_RESULT_QUERY,
            {"result_id": result_id}
        )
        return self._process_result_data(raw_result)

    def _process_result_data(self, raw_result: dict) -> QueryResultData:
        results = raw_result['data']['query_results']
        errors = [blob.get('error').get('error')
                  for blob in results if blob.get('error')]
        if any(errors):
            raise DuneError('.'.join(errors))

        query_result_data = results[0]
        query_result_data['raw_data'] = raw_result['data']['get_result_by_result_id']
        return QueryResultData(**query_result_data)

    def query(self, sql: str, dataset_id: Dataset, parameters: Optional[List[QueryParameter]] = list(), is_temp=False) -> DuneQuery:
        # fail if not logged in
        # make this into its own empty query model class and populate it?
        if self.user_id is None:
            raise DuneError('Must login before querying!')
        object = {
            "dataset_id": dataset_id,
            "description": "",
            "is_archived": False,
            "is_temp": is_temp,
            "name": "New Query blah",
            "query": sql,
            "schedule": None,
            "user_id": self.user_id
        }
        on_conflict = {
            "constraint": "queries_pkey",
            "update_columns": [
                "dataset_id",
                "name",
                "description",
                "query",
                "schedule",
                "is_archived",
                "is_temp",
                "tags",
                "parameters"
            ],
        }
        # self.session_id should be RAND int
        upsert_response = self._post_graph_ql(
            "UpsertQuery",
            UPSERT_QUERY,
            {
                "object": object,
                "on_conflict": on_conflict,
                "session_id": randint(0, 9999)
            }
        )
        query_id = upsert_response["data"]["insert_queries_one"]["id"]

        # TODO maybe retry on this? might not need to
        executed = self._post_graph_ql(
            "ExecuteQuery",
            EXECUTE_QUERY,
            {"parameters": parameters, "query_id": query_id}
        )
        return self.fetch_query(query_id, parameters)

        # Should return a DuneQuery Object, that can be used to grab the table, charts etc
        # Streaming Responses??
    def fetch_query(self, query_id: int, parameters: Optional[List[QueryParameter]] = None) -> DuneQuery:
        metadata = self._fetch_query_metadata(query_id)
        result_id, job_id = self._fetch_result_id(query_id, parameters)
        # TODO raise if both None
        if result_id is None:
            result_data = self._fetch_result_data_by_job(job_id)
        else:
            result_data = self._fetch_result_data_by_result(result_id)
        query = Query(metadata=metadata, result_data=result_data)
        return DuneQuery(query)
