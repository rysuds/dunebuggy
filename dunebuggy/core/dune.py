from uuid import UUID
from httpx import Client
from random import randint
from typing import List, Optional, Dict
from dunebuggy.models.constants import (
    DEFAULT_HEADERS,
    LOGIN_URL,
    CSRF_URL,
    BASE_URL,
    API_AUTH_URL,
    SESSION_URL,
    GRAPH_QL_URL
)
from dunebuggy.models.query import (
    Query, QueryMetadata,
    QueryResultData, QueryParameter,
    CreateQueryOnConflict, CreateQueryObject
)
from dunebuggy.models.constants import DatasetId
from dunebuggy.models.gqlqueries import QueryName
from dunebuggy.core.dunequery import DuneQuery
from dunebuggy.core.exceptions import DuneError


class GraphQLQuerierMixin:

    def _post_graph_ql(self, query_name: QueryName, variables: dict) -> dict:
        # Change this to pydantic data type with enum? I.e. mapping between operation name and query?
        data = {
            "operationName": query_name.value,
            "query": query_name.get_query_string(),
            "variables": variables
        }
        response = self.client.post(GRAPH_QL_URL, json=data)
        return response.json()

    def _get_user_id(self, sub: UUID) -> int:
        user_info = self._post_graph_ql(
            QueryName.FIND_SESSION_USER,
            {"sub": sub}
        )
        return user_info["data"]["users"][0]["id"]

    def _get_query_metadata(self, query_id: int) -> QueryMetadata:
        raw_metadata = self._post_graph_ql(
            QueryName.FIND_QUERY,
            {"id": query_id}
        )
        metadata = raw_metadata['data']['queries'][0]
        return QueryMetadata(**metadata)

    def _get_result_id(self, query_id: int, parameters: Optional[List[QueryParameter]] = None) -> str:
        variables = {"query_id": query_id}
        if parameters is not None:
            parameters = [
                param.dict() for param in parameters if type(param) == QueryParameter]
            variables['parameters'] = parameters
        result_id_data = self._post_graph_ql(
            QueryName.GET_RESULT,
            variables
        )
        result = result_id_data.get('data').get('get_result')
        return result.get('result_id'), result.get('job_id')

    def _get_result_data_by_job(self, job_id: UUID) -> QueryResultData:
        raw_result = self._post_graph_ql(
            QueryName.FIND_RESULT_DATA_BY_JOB,
            {"job_id": job_id}
        )
        return self._process_result_data(raw_result)

    def _get_result_data_by_result(self, result_id: int) -> QueryResultData:
        raw_result = self._post_graph_ql(
            QueryName.FIND_RESULT_DATA_BY_RESULT,
            {"result_id": result_id}
        )
        return self._process_result_data(raw_result)

    def _upsert_query(self, object: CreateQueryObject, on_conflict: CreateQueryOnConflict) -> Dict:
        upsert_response = self._post_graph_ql(
            QueryName.UPSERT_QUERY,
            {
                "object": object.dict(),
                "on_conflict": on_conflict.dict(),
                "session_id": randint(0, 9999)
            }
        )
        return upsert_response

    def _execute_query(self, parameters: list, query_id: int) -> None:
        # TODO maybe retry/raise on this? might not need to
        self._post_graph_ql(
            QueryName.EXECUTE_QUERY,
            {"parameters": parameters, "query_id": query_id}
        )


class Dune(GraphQLQuerierMixin):
    def __init__(self, username=None, password=None):
        self.client = Client()
        self.client.headers.update(DEFAULT_HEADERS)
        self.access_token = None
        self.token = None
        self.sub = None
        self.user_id = None

        if username is not None and password is not None:
            self.login(username, password)

    def login(self, username: str, password: str) -> None:
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
            raise DuneError("Dune Login Failed: Defaulting to No User/Pass")

        self.token = response.json().get('token')
        self.access_token = response.json().get('accessToken')
        self.sub = response.json().get('sub')

        self.client.headers.update(
            {'authorization': f'Bearer {self.token}'}
        )
        self.user_id = self._get_user_id(self.sub)

    def _process_result_data(self, raw_result: dict) -> QueryResultData:
        results = raw_result['data']['query_results']
        errors = [blob.get('error').get('error')
                  for blob in results if blob.get('error')]
        if any(errors):
            raise DuneError('.'.join(errors))

        query_result_data = results[0]
        query_result_data['raw_data'] = raw_result['data']['get_result_by_result_id']
        return QueryResultData(**query_result_data)

    def create_query(self, query_name: str, sql: str, dataset_id: DatasetId, parameters: Optional[List[QueryParameter]] = list(), is_temp=False) -> DuneQuery:
        # fail if not logged in
        # make this into its own empty query model class and populate it?
        # https://github.com/kayak/pypika
        # can cast from str -> sql
        # https://pypika.readthedocs.io/en/latest/_modules/pypika/queries.html#AliasedQuery.get_sql
        if self.user_id is None:
            raise DuneError('Must login before creating a query!')
        object = CreateQueryObject(
            dataset_id=dataset_id,
            is_temp=is_temp,
            name=query_name,
            query=sql,
            user_id=self.user_id
        )
        on_conflict = CreateQueryOnConflict()

        upsert_response = self._upsert_query(object, on_conflict)
        query_id = upsert_response["data"]["insert_queries_one"]["id"]
        self._execute_query(parameters, query_id)

        return self.fetch_query(query_id, parameters)

        # Should return a DuneQuery Object, that can be used to grab the table, charts etc
        # Streaming Responses??
    def fetch_query(self, query_id: int, parameters: Optional[List[QueryParameter]] = None) -> DuneQuery:
        metadata = self._get_query_metadata(query_id)
        result_id, job_id = self._get_result_id(query_id, parameters)
        # TODO raise if both None
        if result_id is None:
            result_data = self._get_result_data_by_job(job_id)
        else:
            result_data = self._get_result_data_by_result(result_id)
        query = Query(metadata=metadata, result_data=result_data)
        return DuneQuery(query)
