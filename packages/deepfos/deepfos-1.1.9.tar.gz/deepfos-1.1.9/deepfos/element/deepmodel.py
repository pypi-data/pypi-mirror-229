from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from typing import List, TYPE_CHECKING, Any, Dict, Iterable, Union, NamedTuple, Tuple

import edgedb
import pandas as pd
from loguru import logger
from pandas.core.dtypes.common import is_datetime64_dtype, is_numeric_dtype
from pydantic import BaseModel, parse_obj_as, ValidationError

from deepfos import OPTION
from deepfos.api.deepmodel import DeepModelAPI
from deepfos.api.models.deepmodel import ObjectBasicDTO, ObjectParam
from deepfos.db.edb import create_async_client
from deepfos.element.base import ElementBase, SyncMeta
from deepfos.exceptions import NonExternalObjectNotExist, ExternalObjectReadOnly, RequiredFieldUnfilled
from deepfos.lib import serutils
from deepfos.lib.asynchronous import future_property, evloop
from deepfos.lib.decorator import flagmethod

__all__ = ['AsyncDeepModel', 'DeepModel', 'OBJECT_QUERY', 'to_structure']

OBJECT_QUERY = \
    """
    with module schema
    select ObjectType {
        name,
        links: {
            name,
            cardinality,
            required,
            target: { name },
            expr,
            constraints: { name, expr, params: { name, @value } },
        },
        properties: {
            name,
            cardinality,
            required,
            target: { name },
            expr,
            constraints: { name, expr, params: { name, @value } },
        },
        external
    }
    """

# 由于json number最大至int32或int64的数字
# 为避免精度缺失，如下类型需转换为string
# 相应Note见:
# https://www.edgedb.com/docs/stdlib/numbers#type::std::bigint
# https://www.edgedb.com/docs/stdlib/numbers#type::std::decimal
NEED_CAST_STR = ['std::bigint', 'std::decimal', ]

_escape_table = [chr(x) for x in range(128)]
_escape_table[ord("'")] = u"\\'"
_escape_table[ord('\\')] = u'\\\\'
_escape_table[0] = ''

DOC_ARGS_KWARGS = """
        Hint:
            
            args语法:
            
                select User{name, is_active} filter .name=<std::str>$0 and is_active=<std::bool>$1
            
            .. admonition:: 使用示例
            
                .. code-block:: python
                
                    dm = DeepModel('mainview')
                    
                    dm.query('select User{name, is_active} filter .name=<std::str>$0 and is_active=<std::bool>$1', 'Alice', 'True')
            
            kwargs语法:
            
                select User{name, is_active} filter .name=<std::str>$name and is_active=<std::bool>$active
            
            .. admonition:: 使用示例
            
                .. code-block:: python
                
                    dm = DeepModel('mainview')
                    
                    dm.execute('delete User filter .name=<std::str>$name and is_active=<std::bool>$active', 
                                name='Alice', active='True')
            
            此处 `$` 为以args/kwargs的方式指定参数的特殊符号，且需在参数前增加相应类型提示
"""


class QueryWithArgs(NamedTuple):
    commands: str
    args: Tuple
    kwargs: Dict[str, Any]


def escape_string(value):
    return value.translate(_escape_table)


class TargetField(BaseModel):
    name: str


class FieldInfo(BaseModel):
    name: str
    target: TargetField
    expr: str = None
    required: bool

    @property
    def field_type(self):
        return self.target.name

    @property
    def computable(self):
        return self.expr is not None


class ObjectTypeFrame(BaseModel):
    name: str
    links: List[FieldInfo]
    properties: List[FieldInfo]
    external: bool

    @property
    def fields(self):
        return {ptr.name: ptr for ptr in [*self.links, *self.properties]}


def scalar_type(field_type):
    return field_type.startswith('std::') or field_type == 'cal::local_datetime'


def _quote_escape(value):
    if pd.isna(value):
        return '{}'
    if not isinstance(value, str):
        return f"'{str(value)}'"
    return f"'{escape_string(value)}'"


def _format_series(series, field_type: Dict[str, str], auto_cast: bool) -> pd.Series:
    cast_type = field_type[series.name]
    prefix = f'{series.name} := <{cast_type}>' if auto_cast else f'{series.name} := '

    if is_datetime64_dtype(series.dtype):
        series = "'" + series.dt.strftime("%Y-%m-%dT%H:%M:%S") + "'"
        return prefix + series.fillna('{}')

    elif not is_numeric_dtype(series.dtype) and scalar_type(cast_type):
        return prefix + series.apply(_quote_escape)

    elif scalar_type(cast_type):
        return prefix + series.fillna('{}').apply(lambda value: str(value))

    return prefix + series.fillna('{}').astype(str, errors='ignore')


def _convert(data: pd.DataFrame, object_name: str, field_type: Dict[str, str], auto_cast):
    if data.empty:
        return ''

    data_df = data.apply(_format_series, field_type=field_type, auto_cast=auto_cast)
    inserts = f"Insert {object_name} {{\n" + pd.Series(data_df.values.tolist()).str.join(', ') + "}"
    return ";\n".join(inserts)


def maybe_cast(series, field_type: Dict[str, str]):
    cast_type = field_type[series.name]

    if is_datetime64_dtype(series.dtype):
        return series.dt.strftime("%Y-%m-%dT%H:%M:%S")

    if cast_type in NEED_CAST_STR:
        series = series.apply(lambda x: str(x) if not pd.isna(x) else x)

    return series


def bulk_insert_by_fields(object_name: str, field_type: Dict[str, str]):
    return f"""
    with raw_data := <json>$data,
    for item in json_array_unpack(raw_data) union (
        insert {object_name} {{
    {', '.join(
        [
            f"{name} := <{cast_type}>"
            f"{'<std::str>' if cast_type in NEED_CAST_STR else ''}"
            f"item['{name}']" for name, cast_type in field_type.items()
        ])
    }
        }}
    )
    """


def _iter_ql(
    data: pd.DataFrame,
    object_name: str,
    field_type: Dict[str, str],
    chunksize: int,
    auto_cast: bool,
) -> Iterable[str]:
    if (nrows := len(data)) == 0:
        return

    if chunksize is None or chunksize > nrows:
        yield _convert(data, object_name, field_type, auto_cast)
    elif chunksize <= 0:
        raise ValueError("chunksize must be greater than 0.")
    else:
        for i in range(0, nrows, chunksize):
            yield _convert(data.iloc[i: i + chunksize], object_name, field_type, auto_cast)


def to_structure(obj: edgedb.Object) -> Dict[str, FieldInfo]:
    if not isinstance(obj, edgedb.Object):
        raise TypeError("预期obj为edgedb.Object")

    serialized = serutils.serialize(obj)

    try:
        return parse_obj_as(ObjectTypeFrame, serialized).fields
    except ValidationError:
        raise TypeError("预期obj为ObjectType查询得到的结构信息")


txn_support = flagmethod('_txn_support_')


class _TxnConfig:
    __slots__ = ('qls', 'in_txn', 'txn_support')

    def __init__(self):
        self.qls = []
        self.in_txn = False
        self.txn_support = False


# -----------------------------------------------------------------------------
# core
class AsyncDeepModel(ElementBase[DeepModelAPI]):
    """DeepModel"""

    def __init__(
        self,
        element_name: str,
        folder_id: str = None,
        path: str = None,
        server_name: str = None,
    ):
        super().__init__(element_name=element_name, folder_id=folder_id, path=path, server_name=server_name)
        self.client = create_async_client(default_module=f"app{OPTION.api.header['app']}")
        self._txn_ = ContextVar('QLTXN')

    def _safe_get_txn_conf(self) -> _TxnConfig:
        try:
            config = self._txn_.get()
        except LookupError:
            config = _TxnConfig()
            self._txn_.set(config)
        return config

    @property
    def _txn_support_(self):
        return self._safe_get_txn_conf().txn_support

    @_txn_support_.setter
    def _txn_support_(self, val):
        self._safe_get_txn_conf().txn_support = val

    @future_property(on_demand=True)
    async def model_objects(self) -> Dict[str, ObjectParam]:
        """MainView中的所有对象详情"""
        api = await self.wait_for('async_api')
        res = await api.object.get_all()
        return {obj.code: obj for obj in res.objectList}

    @future_property(on_demand=True)
    async def model_object_list(self) -> List[ObjectBasicDTO]:
        """MainView中的所有对象列表"""
        api = await self.wait_for('async_api')
        return await api.object.list()

    @future_property(on_demand=True)
    async def user_objects(self) -> Dict[str, edgedb.Object]:
        """当前app下所有的用户对象"""
        objects = await AsyncDeepModel.query_object(
            self,
            f"{OBJECT_QUERY} filter .name like 'app{OPTION.api.header['app']}::%'",
        )
        return {
            obj.name.rpartition('::')[-1]: obj
            for obj in objects
        }

    @future_property(on_demand=True)
    async def system_objects(self) -> Dict[str, edgedb.Object]:
        """当前space下所有的系统对象"""
        objects = await AsyncDeepModel.query_object(
            self,
            f"{OBJECT_QUERY} filter .name like 'space{OPTION.api.header['space']}::%'",
        )
        return {
            obj.name.rpartition('::')[-1]: obj
            for obj in objects
        }

    async def query_object(self, ql: str, *args, **kwargs) -> List[Any]:
        """执行ql查询语句，得到原始结果返回

        如有变量，以args, kwargs的方式提供

        Args:
            ql: 执行的ql
        
        See Also:
        
            :func:`query`, 执行ql查询语句，得到序列化后的结果
            :func:`query_df`, 执行ql查询语句，获取DataFrame格式的二维表
            
        """
        logger.opt(lazy=True).debug(f"Query: [{ql}], \nargs: [{args}], \nkwargs: [{kwargs}].")
        return await self.client.query(ql, *args, **kwargs)

    async def query(self, ql: str, *args, **kwargs) -> List[Any]:
        """执行ql查询语句，得到序列化后的结果

        如有变量，以args, kwargs的方式提供

        Args:
            ql: 执行的ql


        .. admonition:: 示例

            .. code-block:: python

                dm = DeepModel('mainview')

                # 以变量name 查询User对象
                dm.query('select User{name, is_active} filter .name=<std::str>$name', name='Alice')

                # 以占位变量的方式查询User对象
                dm.query('select User{name, is_active} filter .name=<std::str>$0', 'Alice')
        
        See Also:
        
            :func:`query_df`, 执行ql查询语句，获取DataFrame格式的二维表
            :func:`query_object`, 执行ql查询语句，得到原始结果返回

        """
        result = await self.query_object(ql, *args, **kwargs)
        return serutils.serialize(result)

    async def query_df(self, ql: str, *args, **kwargs) -> pd.DataFrame:
        """执行ql查询语句

        获取DataFrame格式的二维表
        如有变量，以arg, kwargs的方式提供

        Args:
            ql: 执行的ql


        .. admonition:: 示例

            .. code-block:: python

                dm = DeepModel('mainview')

                # 以变量name 查询User对象，得到DataFrame
                dm.query_df('select User{name, is_active} filter .name=<std::str>$name', name='Alice')

                # 以占位变量的方式查询User对象，得到DataFrame
                dm.query_df('select User{name, is_active} filter .name=<std::str>$0', 'Alice')
        
        See Also:
        
            :func:`query`, 执行ql查询语句，得到序列化后的结果
            :func:`query_object`, 执行ql查询语句，得到原始结果返回
        
        """

        data = await self.query(ql, *args, **kwargs)
        return pd.DataFrame(data=data)

    query.__doc__ = query.__doc__ + DOC_ARGS_KWARGS
    query_object.__doc__ = query_object.__doc__ + DOC_ARGS_KWARGS
    query_df.__doc__ = query_df.__doc__ + DOC_ARGS_KWARGS

    @txn_support
    async def execute(self, qls: Union[str, List[str], List[QueryWithArgs]], *args, **kwargs):
        """以事务执行多句ql

        Args:
            qls: 要执行的若干ql语句
                 可通过提供QueryWithArgs对象ql的方式定制每句ql的参数信息
                 亦可直接以*args, **kwargs的形式提供参数信息
                 会自动用作所有string形式ql的参数

        """
        if isinstance(qls, str):
            qls_with_args = [QueryWithArgs(qls, args=args, kwargs=kwargs)]
        else:
            qls_with_args = []
            for ql in qls:
                if isinstance(ql, QueryWithArgs):
                    qls_with_args.append(ql)
                elif isinstance(ql, str):
                    qls_with_args.append(QueryWithArgs(ql, args=args, kwargs=kwargs))
                else:
                    raise TypeError(f'qls参数中出现类型非法成员：{type(ql)}')

        await self._run_qls(qls_with_args)

    execute.__doc__ = execute.__doc__ + DOC_ARGS_KWARGS

    async def _execute(self, qls_with_args: List[QueryWithArgs]):
        async for tx in self.client.transaction():
            async with tx:
                for ql in qls_with_args:
                    logger.opt(lazy=True).debug(
                        f"Execute QL: [{ql.commands}], \nargs: [{ql.args}], \nkwargs: [{ql.kwargs}]."
                    )
                    await tx.execute(ql.commands, *ql.args, **ql.kwargs)

    @staticmethod
    def _valid_fields(fields: Iterable[str], structure) -> Tuple[Iterable[str], Dict[str, str]]:
        changeable_fields = set()
        required_fields = set()
        field_type = {}

        for field in structure.values():
            if not field.computable and not field.name.startswith('__') and field.name != 'id':
                changeable_fields.add(field.name)

                if field.name in fields:
                    field_type[field.name] = field.field_type

                if field.required:
                    required_fields.add(field.name)

        if not required_fields.issubset(fields):
            raise RequiredFieldUnfilled(f'缺少必填字段: {required_fields.difference(fields)}')

        return set(fields).intersection(changeable_fields), field_type

    async def _valid_object(self, object_name):
        if object_name in self.user_objects:
            obj = self.user_objects[object_name]
        elif object_name in self.system_objects:
            obj = self.system_objects[object_name]
        else:
            objects = await self.query_object(
                f"{OBJECT_QUERY} filter .name = '{object_name}' and .external = false"
            )
            if len(objects) == 0:
                raise NonExternalObjectNotExist(f'EdgeDB非外部对象[{object_name}]不存在，无法插入数据')

            obj = objects[0]
        if obj.external:
            raise ExternalObjectReadOnly(f'EdgeDB非外部对象[{object_name}]不支持DML')
        return obj

    async def _run_qls(self, qls_with_args: List[QueryWithArgs]):
        txn_conf = self._safe_get_txn_conf()

        if txn_conf.in_txn and self._txn_support_:
            txn_conf.qls.extend(qls_with_args)
            return

        await self._execute(qls_with_args)

    @txn_support
    async def insert_df(
        self,
        object_name: str,
        data: pd.DataFrame,
        chunksize: int = 50,
        auto_cast: bool = True
    ):
        """以事务执行基于DataFrame数据的批量插入数据

        Args:
            object_name: 被插入数据的对象名
            data: 要插入的数据
            chunksize: 单语句最大行数
            auto_cast: 是否在assign值时标注强制类型转换


        .. admonition:: 示例

            .. code-block:: python

                import pandas as pd
                from datetime import datetime

                dm = DeepModel('mainview')

                data = pd.DataFrame(
                    {
                        'p_bool': [True, False],
                        'p_str': ['Hello', 'World'],
                        'p_local_datetime': [datetime(2021, 1, 1, 0, 0, 0), datetime(2021, 2, 1, 0, 0, 0), ],
                    }
                )
                # 将data插入Demo对象
                dm.insert_df('Demo', data)


        See Also:
            :func:`bulk_insert_df`, 以事务执行基于DataFrame字段信息的批量插入数据

        """
        if data.empty:
            logger.info("data为空，无DML执行")
            return

        obj = await self._valid_object(object_name)
        structure = to_structure(obj)
        valid_fields, field_type = self._valid_fields(data.columns, structure)
        data = data[valid_fields]
        await self.execute(list(_iter_ql(data, object_name, field_type, chunksize, auto_cast)))

    @txn_support
    async def bulk_insert_df(
        self,
        object_name: str,
        data: pd.DataFrame,
        chunksize: int = 500,
    ):
        """以事务执行基于DataFrame字段信息的批量插入数据

        Args:
            object_name: 被插入数据的对象名
            data: 要插入的数据
            chunksize: 单次最大行数


        .. admonition:: 示例

            .. code-block:: python

                import pandas as pd
                from datetime import datetime

                dm = DeepModel('mainview')

                data = pd.DataFrame(
                    {
                        'p_bool': [True, False],
                        'p_str': ['Hello', 'World'],
                        'p_local_datetime': [datetime(2021, 1, 1, 0, 0, 0), datetime(2021, 2, 1, 0, 0, 0), ],
                    }
                )
                # 将data插入Demo对象
                dm.bulk_insert_df('Demo', data)


        See Also:
            :func:`insert_df`, 以事务执行基于DataFrame数据的批量插入数据

        """
        if (nrows := len(data)) == 0:
            logger.info("data为空，无DML执行")
            return

        obj = await self._valid_object(object_name)

        structure = to_structure(obj)
        valid_fields, field_type = self._valid_fields(data.columns, structure)

        bulk_ql = bulk_insert_by_fields(object_name, field_type)

        data = data[valid_fields]
        data = data.apply(maybe_cast, field_type=field_type)

        if chunksize is None or chunksize > nrows:
            await self.execute(bulk_ql, data=data.to_json(orient='records'))
        elif chunksize <= 0:
            raise ValueError("chunksize must be greater than 0.")
        else:
            qls = []

            for i in range(0, nrows, chunksize):
                part = data.iloc[i: i + chunksize]
                qls.append(
                    QueryWithArgs(bulk_ql, args=(), kwargs=dict(data=part.to_json(orient='records')))
                )

            await self.execute(qls)

    @asynccontextmanager
    async def start_transaction(self):
        """开启事务

        上下文管理器，使用with语法开启上下文，上下文中的ql将作为事务执行
        退出with语句块后，事务将立即执行，执行过程中如果报错会直接抛出

        .. admonition:: 示例

            .. code-block:: python

                import pandas as pd

                dm = DeepModel('mainview')

                data = pd.DataFrame(
                    {
                        'name': ['Alice', 'Bob', 'Carol'],
                        'deck': [
                            "(SELECT Card FILTER .element IN {'Fire', 'Water'})",
                            "(SELECT Card FILTER .element IN {'Earth', 'Water'})",
                            "(SELECT Card FILTER .element != 'Fire')"
                        ],
                        'awards': [
                            "(SELECT Award FILTER .name IN {'1st', '2nd'})",
                            "(SELECT Award FILTER .name = '3rd')",
                            None
                        ],
                    }
                )

                async with dm.start_transaction():
                    await dm.execute("delete User")
                    await dm.insert_df("User", data)


        Important:

            仅 :func:`insert_df`  :func:`bulk_insert_df` :func:`execute` 方法支持在事务中执行

        """
        try:
            self._txn_.get()
        except LookupError:
            self._txn_.set(_TxnConfig())

        self._txn_.get().in_txn = True

        try:
            yield
            if qls := self._txn_.get().qls:
                await self._execute(qls)
        finally:
            self._txn_.get().in_txn = False


class DeepModel(AsyncDeepModel, metaclass=SyncMeta):
    synchronize = ('query_object', 'query', 'query_df', 'execute', 'insert_df', 'bulk_insert_df')

    if TYPE_CHECKING:  # pragma: no cover
        def query_object(self, ql: str, *args, **kwargs) -> List[Any]:
            ...

        def query(self, ql: str, *args, **kwargs) -> List[Any]:
            ...

        def query_df(self, ql: str, *args, **kwargs) -> pd.DataFrame:
            ...

        def execute(self, qls: Union[str, List[str], List[QueryWithArgs]], *args, **kwargs):
            ...

        def insert_df(
            self,
            object_name: str,
            data: pd.DataFrame,
            chunksize: int = 50,
            auto_cast: bool = True
        ):
            ...

        def bulk_insert_df(
            self,
            object_name: str,
            data: pd.DataFrame,
            chunksize: int = 500,
        ):
            ...

    @contextmanager
    def start_transaction(self):
        """开启事务

        上下文管理器，使用with语法开启上下文，上下文中的ql将作为事务执行
        退出with语句块后，事务将立即执行，执行过程中如果报错会直接抛出

        .. admonition:: 示例

            .. code-block:: python

                import pandas as pd

                dm = DeepModel('mainview')

                data = pd.DataFrame(
                    {
                        'name': ['Alice', 'Bob', 'Carol'],
                        'deck': [
                            "(SELECT Card FILTER .element IN {'Fire', 'Water'})",
                            "(SELECT Card FILTER .element IN {'Earth', 'Water'})",
                            "(SELECT Card FILTER .element != 'Fire')"
                        ],
                        'awards': [
                            "(SELECT Award FILTER .name IN {'1st', '2nd'})",
                            "(SELECT Award FILTER .name = '3rd')",
                            None
                        ],
                    }
                )

                with dm.start_transaction():
                    dm.execute("delete User")
                    dm.insert_df("User", data)


        Important:

            仅 :func:`insert_df`  :func:`bulk_insert_df` :func:`execute` 方法支持在事务中执行

        """
        try:
            self._txn_.get()
        except LookupError:
            self._txn_.set(_TxnConfig())

        self._txn_.get().in_txn = True

        try:
            yield
            if qls := self._txn_.get().qls:
                evloop.run(self._execute(qls))
        finally:
            self._txn_.get().in_txn = False
