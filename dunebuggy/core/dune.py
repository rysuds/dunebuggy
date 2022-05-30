from httpx import Client
from typing import List, Optional
from dunebuggy.models.constants import (
    DEFAULT_HEADERS,
    LOGIN_URL,
    CSRF_URL,
    BASE_URL,
    API_AUTH_URL,
    SESSION_URL
)
from dunebuggy.models.query import (
    Query, QueryParameter,
    CreateQueryOnConflict, CreateQueryObject
)
from dunebuggy.core.gqlquerier import GraphQLQuerier
from dunebuggy.models.constants import DatasetId
from dunebuggy.models.gqlqueries import QueryName
from dunebuggy.core.dunequery import DuneQuery
from dunebuggy.core.exceptions import DuneError


class Dune:
    def __init__(self, username=None, password=None):
        self.client = Client()
        self.gqlquerier = GraphQLQuerier(self.client)
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
        self.user_id = self.gqlquerier.get_user_id(self.sub)

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

        upsert_response = self.gqlquerier.upsert_query(object, on_conflict)
        query_id = upsert_response["data"]["insert_queries_one"]["id"]
        self.gqlquerier.execute_query(parameters, query_id)

        return self.fetch_query(query_id, parameters)

        # Should return a DuneQuery Object, that can be used to grab the table, charts etc
        # Streaming Responses??
    def fetch_query(self, query_id: int, parameters: Optional[List[QueryParameter]] = list()) -> DuneQuery:
        metadata = self.gqlquerier.get_query_metadata(query_id)
        if not parameters and metadata.parameters:
            parameters = metadata.parameters
        result_id, job_id = self.gqlquerier.get_result_id(query_id, parameters)

        # For custom param queries, override default parameters returned by metadata
        if len(parameters):
            metadata.parameters = parameters
        # TODO raise if both None
        if result_id is None:
            result_data = self.gqlquerier.get_result_data_by_job(job_id)
        else:
            result_data = self.gqlquerier.get_result_data_by_result(result_id)
        query = Query(metadata=metadata, result_data=result_data)
        return DuneQuery(query)
