from uuid import UUID
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, AnyHttpUrl

from dunebuggy.models.constants import DatasetId, ParameterEnum, DatasetId


class User(BaseModel):
    id: int
    name: str
    profile_image_url: Optional[AnyHttpUrl]

    @property
    def handle(self) -> str:
        return f'@{self.name}'


class QueryParameter(BaseModel):
    key: str
    type: Optional[ParameterEnum]
    value: str
    enumOptions: Optional[List[str]]

    class Config:
        use_enum_values = True


class QueryMetadata(BaseModel):
    id: int
    name: str
    description: str
    user: User
    query: str  # SQL
    # https://sqlparse.readthedocs.io/en/latest/#:~:text=sqlparse%20is%20a%20non%2Dvalidating,of%20the%20New%20BSD%20license.
    parameters: List[QueryParameter]
    created_at: datetime
    updated_at: datetime


class RawRow(BaseModel):
    data: Dict
    __typename: str


class QueryResultData(BaseModel):
    id: UUID
    job_id: UUID
    runtime: int  # seconds
    generated_at: datetime
    columns: List[str]
    raw_data: List[RawRow]


class Query(BaseModel):
    metadata: QueryMetadata
    result_data: QueryResultData


class CreateQueryObject(BaseModel):
    dataset_id: DatasetId
    is_temp: bool
    name: str
    query: str  # SQL string
    user_id: int

    schedule: Optional[str] = None
    description: str = ""
    is_archived: bool = False
    is_temp: bool

    class Config:
        use_enum_values = True


class CreateQueryOnConflict(BaseModel):
    constraint: str = "queries_pkey"
    update_columns: List[str] = [
        "dataset_id",
        "name",
        "description",
        "query",
        "schedule",
        "is_archived",
        "is_temp",
        "tags",
        "parameters"
    ]
