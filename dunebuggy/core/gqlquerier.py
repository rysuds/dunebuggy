from typing import Dict, List, Optional
from uuid import UUID

from httpx import Client

from dunebuggy.core.exceptions import DuneError
from dunebuggy.models.constants import APP_API_URL, GRAPH_QL_URL
from dunebuggy.models.gqlqueries import QueryName
from dunebuggy.models.query import (
    CreateQueryObject,
    CreateQueryOnConflict,
    QueryMetadata,
    QueryParameter,
    QueryResultData,
)


class GraphQLQuerier:
    def __init__(self, client: Client):
        self.client = client

    def post_graph_ql(
        self, query_name: QueryName, variables: dict, url: str = GRAPH_QL_URL
    ) -> dict:
        # Change this to pydantic data type with enum? I.e. mapping between operation name and query?
        data = {
            "operationName": query_name.value,
            "query": query_name.get_query_string(),
            "variables": variables,
        }
        response = self.client.post(url, json=data)
        response_json = response.json()

        # TODO make this a more general handling pattern for all gql calls
        #   Could make this 'errors' response its own object
        if "errors" in response_json:
            for error in response_json["errors"]:
                # This is hacky and raising on teh first error only, improve this to
                #   return ALL errors from server in one DuneError (DuneMultiError?)
                raise DuneError(
                    f"Dune query failed with code: {error.get('code')} and message: {error.get('message')}"
                )
        return response_json

    def get_user_id(self, sub: UUID) -> int:
        user_info = self.post_graph_ql(QueryName.FIND_SESSION_USER, {"sub": sub})
        return user_info["data"]["users"][0]["id"]

    def get_query_metadata(self, query_id: int, user_id: int) -> QueryMetadata:
        variables = {"id": query_id, "session_filter": {"_eq": user_id}}
        raw_metadata = self.post_graph_ql(QueryName.FIND_QUERY, variables)
        metadata = raw_metadata["data"]["queries"][0]
        return QueryMetadata(**metadata)

    # TODO clean up this bulky handling of parmeters!!
    def get_result_id(
        self, query_id: int, parameters: Optional[List[QueryParameter]] = None
    ) -> str:
        variables = {"query_id": query_id}
        if len(parameters):
            parameters = [
                param.dict(exclude_none=True)
                for param in parameters
                if type(param) == QueryParameter
            ]
        else:
            parameters = list()
        variables["parameters"] = parameters
        result_id_data = self.post_graph_ql(QueryName.GET_RESULT, variables)
        result = result_id_data.get("data").get("get_result_v3")
        return result.get("result_id"), result.get("job_id")

    def upsert_query(
        self,
        object: CreateQueryObject,
        on_conflict: CreateQueryOnConflict,
        user_id: int,
    ) -> Dict:
        upsert_response = self.post_graph_ql(
            QueryName.UPSERT_QUERY,
            {
                "object": object.dict(),
                "on_conflict": on_conflict.dict(),
                "session_id": user_id,
            },
        )
        return upsert_response

    def execute_query(self, parameters: list, query_id: int) -> None:
        # TODO maybe retry/raise on this? might not need to
        # TODO clean up gross parameters handling
        parameters = [
            param.dict() for param in parameters if type(param) == QueryParameter
        ]
        self.post_graph_ql(
            QueryName.EXECUTE_QUERY, {"query_id": query_id, "parameters": parameters}
        )

    def get_execution(
        self, execution_id: str, parameters: list, query_id: int
    ) -> QueryResultData:
        variables = {
            "execution_id": execution_id,
            "parameters": parameters,
            "query_id": query_id,
        }
        raw_result = self.post_graph_ql(
            QueryName.GET_EXECUTION, variables=variables, url=APP_API_URL
        )
        return self.process_result_data(raw_result)

    def process_result_data(self, raw_result: dict) -> QueryResultData:
        # TODO error raise on other execution failures
        # execution_failed, execution_queued, execution_running, execution_succeeded
        execution_status = raw_result["data"]["get_execution"]
        succeeded_data = execution_status.get("execution_succeeded")
        if succeeded_data is None:
            raise Error("Execution failed!")

        return QueryResultData(**succeeded_data)
