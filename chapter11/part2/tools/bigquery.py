import pandas as pd
import streamlit as st
from typing import Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from langchain_core.tools import Tool, StructuredTool
from langchain_core.pydantic_v1 import (BaseModel, Field)
from src.code_interpreter import CodeInterpreterClient

class SqlTableInfoInput(BaseModel):
    table_name: str = Field()

class ExecSqlInput(BaseModel):
    query: str = Field()
    limit: Optional[int] = Field(default=None)

class BigQueryClient:
    def __init__(
        self,
        code_interpreter: CodeInterpreterClient,
        project_id: str = 'ai-app-book-bq',
        dataset_project_id: str = 'bigquery-public-data',
        dataset_id: str = 'google_trends',
    ) -> None:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        self.client = bigquery.Client(
            credentials=credentials, project=project_id
        )
        self.dataset_project_id = dataset_project_id
        self.dataset_id = dataset_id
        self.table_names_str = self._fetch_table_names()
        self.code_interpter = code_interpreter
    
    def _fetch_table_names(self) -> str:
        """
        利用可能なテーブル名をBigQueryから取得
        カンマ区切りの文字列として返却
        """
        query = f"""
        SELECT table_name
        FROM `{self.dataset_project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES`
        """
        table_names = self._exec_query(query).table_name.tolist()
        return ', '.join(table_names)
    
    def _exec_query(self, query: str, limit: int = None) -> pd.DataFrame:
        """SQLを実行し Pandas Dataframe として返却"""
        if limit is not None:
            query += f"\nLIMIT {limit}"
        query_job = self.client.query(query)
        return query_job.result().to_dataframe(
            create_bqstorage_client=True
        )