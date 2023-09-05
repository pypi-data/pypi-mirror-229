"""PostgreSQL客户端"""
from functools import cached_property
from typing import Union, List, Iterable, TYPE_CHECKING

import numpy as np
from cachetools import TTLCache
import pandas as pd
from pandas.core.dtypes.common import is_datetime64_dtype, is_numeric_dtype

from deepfos.api.datatable import PostgreSQLAPI
from deepfos.lib.utils import cachedclass
from deepfos.lib.decorator import singleton
from .dbkits import BaseSqlParser, SyncMeta, T_DataInfo, DataframeSQLConvertor, null, _quote_escape
from .connector import PostgreSQLAPIConnector
from .mysql import _AbsAsyncMySQLClient  # noqa


__all__ = [
    'PostgreSQLClient',
    'AsyncPostgreSQLClient',
    '_AsyncPostgreSQLClient',
    'PostgreSQLConvertor',
]


@singleton
class SqlParser(BaseSqlParser):
    api_cls = PostgreSQLAPI

    @cached_property
    def datatable_cls(self):
        from deepfos.element.datatable import AsyncDataTablePostgreSQL
        return AsyncDataTablePostgreSQL


class PostgreSQLConvertor(DataframeSQLConvertor):
    def iter_sql(
        self,
        dataframe: pd.DataFrame,
        tablename: str,
        updatecol: Iterable = None,
        chunksize: int = None,
        conflict_target: Iterable[str] = None,
    ) -> Iterable[str]:
        """ :class:`DataFrame` 对象转换为sql生成器

        如果传了updatecol，将使用 ``INSERT INTO ON CONFLICT`` 语法

        Args:
            dataframe: 待插入数据
            tablename: 数据库表名
            updatecol: 更新的列
            chunksize: 单条sql对应的最大dataframe行数
            conflict_target: 使用INSERT INTO ON CONFLICT语法时的conflict基准列信息

        Returns:
            sql语句生成器

        See Also:
            :func:`df_to_sql`

        """
        # 获取sql
        if (nrows := len(dataframe)) == 0:
            return

        if chunksize is None or chunksize > nrows:
            yield self.convert(dataframe, tablename, updatecol, conflict_target)
        elif chunksize <= 0:
            raise ValueError("chunksize must be greater than 0.")
        else:
            for i in range(0, nrows, chunksize):
                yield self.convert(dataframe.iloc[i: i + chunksize], tablename, updatecol, conflict_target)

    def convert(
        self,
        dataframe: pd.DataFrame,
        tablename: str,
        updatecol: Iterable[str] = None,
        conflict_target: Iterable[str] = None,
    ) -> str:
        """ :class:`DataFrame` 对象转换为插库sql

        如果传了updatecol，将使用 ``INSERT INTO ON CONFLICT`` 语法

        Args:
            dataframe: 待插入数据
            tablename: 数据库表名
            updatecol: 更新的列
            conflict_target: 使用INSERT INTO ON CONFLICT语法时的conflict基准列信息

        Returns:
            sql语句

        See Also:
            如果单条sql语句太长导致无法入库，可以使用 :func:`gen_sql`，
            指定 ``chuncksize`` ，该方法将把一条较大的sql拆分成多条执行。

        """
        if dataframe.empty:
            return ''

        data_df = dataframe.copy()
        # 获取日期型与非数字型的列
        datetime_col = [is_datetime64_dtype(x) for x in data_df.dtypes]  # 获取日期型的列
        # 对日期型重置格式到秒级别
        data_df.loc[:, datetime_col] = data_df.loc[:, datetime_col] \
            .apply(lambda x: np.where(x.isna(), np.NAN, self.format_datetime(x)))

        # 空值填充
        data_df = data_df.fillna(null)
        # 获取非数字型的列
        str_like_cols = [
            (not (is_numeric_dtype(x) or is_datetime))
            for x, is_datetime in zip(data_df.dtypes, datetime_col)
        ]
        # 对字符串型列转义，加引号
        data_df.loc[:, str_like_cols] = data_df.loc[:, str_like_cols].applymap(_quote_escape)
        # 全部转化为字符串类型
        data_df = data_df.astype(str, errors='ignore')
        values = "(" + pd.Series(data_df.values.tolist()).str.join(',') + ")"
        columns = self.build_column_string(dataframe.columns)
        return self.build_sql(columns, values, tablename, updatecol, conflict_target)

    def build_sql(
        self,
        columns: str,
        values_in_line: Iterable[str],
        tablename: str,
        updatecol: Iterable[str] = None,
        conflict_target: Iterable[str] = None,
    ):
        values = ','.join(values_in_line)
        if updatecol is None:
            return f'INSERT INTO {self.quote_char}{tablename}{self.quote_char} ({columns}) VALUES {values}'

        update_str = ','.join([f"{x}=EXCLUDED.{x}" for x in updatecol])
        if not update_str:
            return f'INSERT INTO {self.quote_char}{tablename}{self.quote_char} ({columns}) VALUES {values}'

        if conflict_target is None:
            raise ValueError('如需使用ON CONFLICT DO UPDATE语法，'
                             '需提供有唯一约束的列作为conflict_target列信息')

        conflict_target_clause = ",".join(conflict_target)

        if conflict_target_clause:
            conflict_target_clause = f"({conflict_target_clause})"

        return f'INSERT INTO {self.quote_char}{tablename}{self.quote_char} ({columns}) ' \
               f'VALUES {values} ' \
               f'ON CONFLICT {conflict_target_clause} ' \
               f'DO UPDATE SET {update_str}'


# -----------------------------------------------------------------------------
# core
class _AsyncPostgreSQLClient(_AbsAsyncMySQLClient):
    convertor = PostgreSQLConvertor(quote_char="")

    def __init__(self, version: Union[float, str] = None):  # noqa
        self.parser = SqlParser()
        self.connector = PostgreSQLAPIConnector(version)

    async def insert_df(
        self,
        dataframe: pd.DataFrame,
        element_name: str = None,
        table_name: str = None,
        updatecol: Iterable[str] = None,
        table_info: T_DataInfo = None,
        chunksize: int = None,
        conflict_target: Iterable[str] = None,
    ):
        """将 :class:`DataFrame` 的插入数据表

        Args:
            dataframe: 入库数据
            element_name: 数据表元素名
            table_name: 数据表的 **实际表名**
            updatecol: 更新的列 (用于INSERT INTO ON CONFLICT)
            table_info: 数据表元素信息，使用table
            chunksize: 单次插库的数据行数
            conflict_target: 使用INSERT INTO ON CONFLICT语法时的约束列信息

        """
        if table_name is not None:
            tbl_name = table_name
        elif element_name is not None:
            tbl_name = (await self.parser.parse(["${%s}" % element_name], table_info))[0]
        else:
            raise ValueError("Either 'element_name' or 'table_name' must be presented.")

        sqls = list(self.convertor.iter_sql(
            dataframe, tbl_name, updatecol=updatecol, chunksize=chunksize, conflict_target=conflict_target
        ))
        return await self.connector.trxn_execute(sqls)


class _PostgreSQLClient(_AsyncPostgreSQLClient, metaclass=SyncMeta):
    synchronize = (
        'exec_sqls',
        'query_dfs',
        'insert_df',
    )

    if TYPE_CHECKING:  # pragma: no cover
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
class AsyncPostgreSQLClient(_AsyncPostgreSQLClient):
    pass


@cachedclass(TTLCache(maxsize=5, ttl=3600))
class PostgreSQLClient(_PostgreSQLClient):
    pass
