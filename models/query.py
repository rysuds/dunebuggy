import datetime

from uuid import UUID
from typing import Optional, List, Dict
from pydantic import BaseModel, AnyHttpUrl


class User(BaseModel):
    id: int
    name: str
    profile_image_url: Optional[AnyHttpUrl]

    @property
    def handle(self) -> str:
        return f'@{self.handle}'


class QueryMetadata(BaseModel):
    id: int
    name: str
    description: str
    user: User
    query: str  # SQL
    # https://sqlparse.readthedocs.io/en/latest/#:~:text=sqlparse%20is%20a%20non%2Dvalidating,of%20the%20New%20BSD%20license.
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
