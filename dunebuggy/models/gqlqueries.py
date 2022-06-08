from enum import Enum
from typing import Dict
from pydantic import BaseModel

# QueryString var names should be QueryName name + _QUERY


class QueryString(str, Enum):
    FIND_QUERY_QUERY = "query FindQuery($session_id: Int, $id: Int!, $favs_last_24h: Boolean! = false, $favs_last_7d: Boolean! = false, $favs_last_30d: Boolean! = false, $favs_all_time: Boolean! = true) {\n  queries(where: {id: {_eq: $id}}) {\n    ...Query\n    favorite_queries(where: {user_id: {_eq: $session_id}}, limit: 1) {\n      created_at\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Query on queries {\n  ...BaseQuery\n  ...QueryVisualizations\n  ...QueryForked\n  ...QueryUsers\n  ...QueryFavorites\n  __typename\n}\n\nfragment BaseQuery on queries {\n  id\n  dataset_id\n  name\n  description\n  query\n  is_private\n  is_temp\n  is_archived\n  created_at\n  updated_at\n  schedule\n  tags\n  parameters\n  __typename\n}\n\nfragment QueryVisualizations on queries {\n  visualizations {\n    id\n    type\n    name\n    options\n    created_at\n    __typename\n  }\n  __typename\n}\n\nfragment QueryForked on queries {\n  forked_query {\n    id\n    name\n    user {\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment QueryUsers on queries {\n  user {\n    ...User\n    __typename\n  }\n  __typename\n}\n\nfragment User on users {\n  id\n  name\n  profile_image_url\n  __typename\n}\n\nfragment QueryFavorites on queries {\n  query_favorite_count_all @include(if: $favs_all_time) {\n    favorite_count\n    __typename\n  }\n  query_favorite_count_last_24h @include(if: $favs_last_24h) {\n    favorite_count\n    __typename\n  }\n  query_favorite_count_last_7d @include(if: $favs_last_7d) {\n    favorite_count\n    __typename\n  }\n  query_favorite_count_last_30d @include(if: $favs_last_30d) {\n    favorite_count\n    __typename\n  }\n  __typename\n}\n"
    GET_RESULT_QUERY = "query GetResult($query_id: Int!, $parameters: [Parameter!]) {\n  get_result_v2(query_id: $query_id, parameters: $parameters) {\n    job_id\n    result_id\n    error_id\n    __typename\n  }\n}\n"
    FIND_RESULT_DATA_BY_RESULT_QUERY = "query FindResultDataByResult($result_id: uuid!) {\n  query_results(where: {id: {_eq: $result_id}}) {\n    id\n    job_id\n    error\n    runtime\n    generated_at\n    columns\n    __typename\n  }\n  get_result_by_result_id(args: {want_result_id: $result_id}) {\n    data\n    __typename\n  }\n}\n"
    UPSERT_QUERY_QUERY = "mutation UpsertQuery($session_id: Int!, $object: queries_insert_input!, $on_conflict: queries_on_conflict!, $favs_last_24h: Boolean! = false, $favs_last_7d: Boolean! = false, $favs_last_30d: Boolean! = false, $favs_all_time: Boolean! = true) {\n  insert_queries_one(object: $object, on_conflict: $on_conflict) {\n    ...Query\n    favorite_queries(where: {user_id: {_eq: $session_id}}, limit: 1) {\n      created_at\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Query on queries {\n  ...BaseQuery\n  ...QueryVisualizations\n  ...QueryForked\n  ...QueryUsers\n  ...QueryFavorites\n  __typename\n}\n\nfragment BaseQuery on queries {\n  id\n  dataset_id\n  name\n  description\n  query\n  is_private\n  is_temp\n  is_archived\n  created_at\n  updated_at\n  schedule\n  tags\n  parameters\n  __typename\n}\n\nfragment QueryVisualizations on queries {\n  visualizations {\n    id\n    type\n    name\n    options\n    created_at\n    __typename\n  }\n  __typename\n}\n\nfragment QueryForked on queries {\n  forked_query {\n    id\n    name\n    user {\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment QueryUsers on queries {\n  user {\n    ...User\n    __typename\n  }\n  __typename\n}\n\nfragment User on users {\n  id\n  name\n  profile_image_url\n  __typename\n}\n\nfragment QueryFavorites on queries {\n  query_favorite_count_all @include(if: $favs_all_time) {\n    favorite_count\n    __typename\n  }\n  query_favorite_count_last_24h @include(if: $favs_last_24h) {\n    favorite_count\n    __typename\n  }\n  query_favorite_count_last_7d @include(if: $favs_last_7d) {\n    favorite_count\n    __typename\n  }\n  query_favorite_count_last_30d @include(if: $favs_last_30d) {\n    favorite_count\n    __typename\n  }\n  __typename\n}\n"
    EXECUTE_QUERY_QUERY = "mutation ExecuteQuery($query_id: Int!, $parameters: [Parameter!]!) {\n  execute_query(query_id: $query_id, parameters: $parameters) {\n    job_id\n    __typename\n  }\n}\n"
    FIND_SESSION_USER_QUERY = "query FindSessionUser($sub: uuid!) {\n  users(where: {private_info: {cognito_id: {_eq: $sub}}}) {\n    ...SessionUser\n    __typename\n  }\n}\n\nfragment SessionUser on users {\n  id\n  name\n  profile_image_url\n  private_info {\n    stripeCustomerId: stripe_customer_id\n    is_pro\n    permissions\n    __typename\n  }\n  __typename\n}\n"
    FIND_RESULT_DATA_BY_JOB_QUERY = "query FindResultDataByJob($job_id: uuid!) {\n  query_results(where: {job_id: {_eq: $job_id}, error: {_is_null: true}}) {\n    id\n    job_id\n    runtime\n    generated_at\n    columns\n    __typename\n  }\n  query_errors(where: {job_id: {_eq: $job_id}}) {\n    id\n    job_id\n    runtime\n    message\n    metadata\n    type\n    generated_at\n    __typename\n  }\n  get_result_by_job_id(args: {want_job_id: $job_id}) {\n    data\n    __typename\n  }\n}\n"


class QueryName(str, Enum):
    FIND_SESSION_USER = "FindSessionUser"
    FIND_QUERY = "FindQuery"
    GET_RESULT = "GetResult"
    FIND_RESULT_DATA_BY_JOB = "FindResultDataByJob"
    FIND_RESULT_DATA_BY_RESULT = "FindResultDataByResult"
    UPSERT_QUERY = "UpsertQuery"
    EXECUTE_QUERY = "ExecuteQuery"

    def get_query_string(self) -> str:
        return getattr(QueryString, f"{self.name}_QUERY").value


class GQLPostBlob(BaseModel):
    operationName: QueryName
    query: QueryString
    variables: Dict

    class Config:
        use_enum_values = True
