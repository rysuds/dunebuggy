import pandas as pd

from typing import List, Dict
from dunebuggy.models.query import (
    Query, QueryMetadata, QueryParameter, QueryResultData,
    RawRow
)


class DuneQuery:
    def __init__(self, query: Query):
        self.metadata: QueryMetadata = query.metadata
        self.result_data: QueryResultData = query.result_data
        self._df = None

    def __repr__(self) -> str:
        return f'<DuneQuery query_id={self.query_id} name={self.name} length={self.length} rows>'

    @property
    def query_id(self) -> int:
        return self.metadata.id

    @property
    def result_id(self):
        return self.result_data.id

    @property
    def job_id(self):
        return self.result_data.job_id

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def length(self) -> int:
        return len(self.result_data.raw_data)

    @property
    def author(self) -> str:
        return self.metadata.user.handle

    @property
    def columns(self) -> List[str]:
        return self.result_data.columns

    @property
    def raw(self) -> List[RawRow]:
        return self.result_data.raw_data

    @property
    def parameters(self) -> List[QueryParameter]:
        return self.metadata.parameters

    @property
    def raw_sql(self) -> str:
        return self.metadata.query

    @property
    def df(self) -> pd.DataFrame:
        # ad-hoc caching
        if self._df is None:
            self._df = self._process_to_df(self.raw)
        return self._df

    @property
    def info(self) -> Dict:
        return {
            'name': self.name,
            'author': self.author,
            'length': self.length,
            'query_id': self.query_id,
            'result_id': self.result_id,
            'job_id': self.job_id,
            'columns': self.columns
        }

    def _process_to_df(self, results: List) -> pd.DataFrame:
        processed = [r.data for r in results]
        return pd.DataFrame(processed)

    def to_csv(self, filename: str) -> None:
        return self.df.to_csv(filename)
