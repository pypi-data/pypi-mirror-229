"""Dameng客户端"""
import asyncio
from functools import cached_property
from typing import Union, List, Iterable, TYPE_CHECKING

from cachetools import TTLCache
import pandas as pd

from deepfos.api.datatable import DaMengAPI
from deepfos.lib.utils import cachedclass
from deepfos.db.oracle import OracleDFSQLConvertor, SqlParser as OracleSqlParser
from .dbkits import SyncMeta, T_DataInfo
from .connector import DaMengAPIConnector
from .mysql import _AbsAsyncMySQLClient  # noqa


__all__ = [
    'DaMengClient',
    'AsyncDaMengClient',
]


class SqlParser(OracleSqlParser):
    api_cls = DaMengAPI

    @cached_property
    def datatable_cls(self):
        from deepfos.element.datatable import DataTableDaMeng
        return DataTableDaMeng

    @staticmethod
    async def query_table_names(api: DaMengAPI, query_table):
        return await OracleSqlParser.query_table_names(api, query_table)


# -----------------------------------------------------------------------------
# core
class _AsyncDaMengClient(_AbsAsyncMySQLClient):
    convertor = OracleDFSQLConvertor(quote_char='"')

    def __init__(self, version: Union[float, str] = None):  # noqa
        self.parser = SqlParser()
        self.connector = DaMengAPIConnector(version)


class _DaMengClient(_AsyncDaMengClient, metaclass=SyncMeta):
    synchronize = (
        'exec_sqls',
        'query_dfs',
        'insert_df',
    )

    if TYPE_CHECKING:
        def exec_sqls(
            self,
            sqls: Union[str, Iterable[str]],
            table_info: T_DataInfo = None
        ):
            ...

        def query_dfs(
            self,
            sqls: Union[str, Iterable[str]],
            table_info: T_DataInfo = None
        ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
            ...

        def insert_df(
            self,
            dataframe: pd.DataFrame,
            element_name: str = None,
            table_name: str = None,
            updatecol: Iterable[str] = None,
            table_info: T_DataInfo = None,
            chunksize: int = None,
        ):
            ...


@cachedclass(TTLCache(maxsize=5, ttl=3600))
class AsyncDaMengClient(_AsyncDaMengClient):
    pass


@cachedclass(TTLCache(maxsize=5, ttl=3600))
class DaMengClient(_DaMengClient):
    pass
