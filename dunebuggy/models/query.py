from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel

from dunebuggy.models.constants import DatasetId, ParameterEnum


class User(BaseModel):
    id: int
    name: str
    profile_image_url: Optional[AnyHttpUrl]

    @property
    def handle(self) -> str:
        return f"@{self.name}"


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


class QueryResultData(BaseModel):
    execution_id: str
    runtime_seconds: int  # seconds
    generated_at: datetime
    columns: List[str]
    data: List[dict]


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
        "is_private",
        "tags",
        "parameters",
    ]
