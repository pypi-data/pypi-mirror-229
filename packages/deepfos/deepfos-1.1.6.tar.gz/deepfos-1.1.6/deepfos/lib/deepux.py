"""DeepUX组件数据源"""
import asyncio
import functools
from typing import Dict, Type

import pandas as pd

from deepfos import OPTION
from deepfos.api.models import BaseModel

__all__ = [
    'BaseField',
    'String',
    'Integer',
    'Boolean',
    'Json',
    'Float',
    'DateTime',
    'UUID',
    'as_datasource',
    'Struct',
]

FLAG_FOR_META = 'describe'
FIELDS = "fields"
STRUCT_FIELD = "objectInfos"
ELE_INFO_FIELD = "elementInfo"
DATA_FIELD = "json"


class BaseField(BaseModel):
    name: str = None
    type: str = None

    def __init__(self, name: str = None, **data):
        super().__init__(name=name, **data)

    def to_dict(self) -> Dict:
        return self.dict()


class String(BaseField):
    """文本"""
    type = 'str'


class Integer(BaseField):
    """整数"""
    type = 'int'


class Boolean(BaseField):
    """布尔"""
    type = 'bool'


class Json(BaseField):
    """多语言文本（json）"""
    type = 'json'


class Float(BaseField):
    """小数"""
    type = 'float'


class DateTime(BaseField):
    """日期时间"""
    type = 'datetime'


class UUID(BaseField):
    """uuid"""
    type = 'uuid'


class StructMeta(type):
    def __new__(mcs, cls_name, bases, namespace: dict):
        fields = []

        for field_name, anno in namespace.get('__annotations__', {}).items():
            if isinstance(anno, type) and issubclass(anno, BaseField) and field_name not in namespace:
                fields.append(anno(name=field_name))

        for k, v in dict(namespace).items():
            if isinstance(v, BaseField):
                namespace.pop(k)
                if v.name is None:
                    v.name = k
                fields.append(v)

        namespace['fields'] = fields

        return super().__new__(mcs, cls_name, bases, namespace)


class Struct(metaclass=StructMeta):
    """数据源字段信息结构

    .. admonition:: 示例

        .. code-block:: python

            from deepfos.lib.deepux import Struct

            class Data(Struct):
                # 声明字段 text 为str类型
                text = String()
                # 声明字段 int1 为int类型
                integer = Integer('int1')
                # 声明字段 float_ 为float类型
                float_: Float
                # 声明字段 dt 为datetime类型
                datetime = DateTime(name='dt')

    See Also:
        :meth:`as_datasource`

    """

    @classmethod
    def to_dict(cls):
        return {
            ELE_INFO_FIELD: {'description': OPTION.general.task_info.get('element_desc', {})},
            STRUCT_FIELD: [
                {
                    FIELDS: [field.to_dict() for field in cls.fields]
                }
            ]
        }


def _resolve_param(args: tuple):
    if len(args) == 2:
        return args[1]
    if len(args) == 1:
        return args[0]
    raise ValueError("Bad signature for main function.")


def as_datasource(
    func=None,
    struct: Type[Struct] = None,
):
    """用作DeepUX数据源的main函数装饰器

    Args:
        func: 返回pandas DataFrame的main方法
        struct: 定义字段及其字段类型的类名称，必填

    .. admonition:: 用法示例

        .. code-block:: python

            from deepfos.lib.deepux import as_datasource, Struct

            # 声明结构信息
            class Data(Struct):
                ...

            @as_datasource(struct=Data)
            def main(p2):
                ...

    See Also:
        :class:`Struct`

    """
    if func is None:
        return functools.partial(as_datasource, struct=struct)

    if struct is None:
        raise ValueError("需定义DeepUX数据源的字段信息")

    if not issubclass(struct, Struct):
        raise ValueError("DeepUX数据源的字段信息需为Struct的子类")

    if asyncio.iscoroutinefunction(func):
        async def wrapper(*args):
            param = _resolve_param(args)

            if param == FLAG_FOR_META:
                return struct.to_dict()

            df = await func(*args)

            assert isinstance(df, pd.DataFrame), '预期main函数返回值为pandas DataFrame'

            return {DATA_FIELD: df.to_dict('records')}
    else:
        def wrapper(*args):
            param = _resolve_param(args)

            if param == FLAG_FOR_META:
                return struct.to_dict()

            df = func(*args)

            assert isinstance(df, pd.DataFrame), '预期main函数返回值为pandas DataFrame'

            return {DATA_FIELD: df.to_dict('records')}

    return functools.wraps(func)(wrapper)
