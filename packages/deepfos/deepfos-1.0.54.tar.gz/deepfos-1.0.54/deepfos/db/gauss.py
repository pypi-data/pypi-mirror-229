"""Gauss客户端"""
from functools import cached_property
from typing import Union, List, Iterable, TYPE_CHECKING

from cachetools import TTLCache
import pandas as pd

from deepfos.api.datatable import GaussAPI
from deepfos.lib.utils import cachedclass
from deepfos.lib.decorator import singleton
from .dbkits import BaseSqlParser, SyncMeta, T_DataInfo
from .connector import GaussAPIConnector
from .mysql import _AbsAsyncMySQLClient  # noqa
from .postgresql import _AsyncPostgreSQLClient


__all__ = [
    'GaussClient',
    'AsyncGaussClient',
]


@singleton
class SqlParser(BaseSqlParser):
    api_cls = GaussAPI

    @cached_property
    def datatable_cls(self):
        from deepfos.element.datatable import DataTableGauss
        return DataTableGauss


# -----------------------------------------------------------------------------
# core
class _AsyncGaussClient(_AsyncPostgreSQLClient):
    def __init__(self, version: Union[float, str] = None):  # noqa
        self.parser = SqlParser()
        self.connector = GaussAPIConnector(version)


class _GaussClient(_AsyncGaussClient, metaclass=SyncMeta):
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
            conflict_target: Iterable[str] = None,
        ):
            ...


@cachedclass(TTLCache(maxsize=5, ttl=3600))
class AsyncGaussClient(_AsyncGaussClient):
    pass


@cachedclass(TTLCache(maxsize=5, ttl=3600))
class GaussClient(_GaussClient):
    pass
