import functools
import inspect

from deepfos.api.app import AppAPI
from deepfos.api.base import DynamicRootAPI
from deepfos.api.models.app import (
    QueryElementInfoByTypeDto as ElementModel,
    ElementRelationInfo, ModuleServerNameVO
)
from deepfos.exceptions import *
from deepfos.lib.constant import RE_SERVER_NAME_PARSER, RE_MODULEID_PARSER
from deepfos.options import OPTION

from typing import Type, Union, Dict, List

__all__ = ['ElementBase', 'AsyncElementBase']


_HINT = """
    如果不提供folder_id和path，将会使用元素名和元素类型进行全局搜索。
    如果找到 **唯一匹配** 的元素，那么一切正常，否则将会报错。
"""

_ARGS = {
    "element_name": "数据表元素名",
    "folder_id": "元素所在的文件夹id",
    "path": "元素所在的文件夹绝对路径",
}

T_ElementInfoWithServer = Union[ModuleServerNameVO, ElementRelationInfo]


class _AppendDoc(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        cls_doc = mcs._split_doc(cls.__doc__)
        cls.__doc__ = mcs._recover_doc(cls_doc)
        return cls

    @staticmethod
    def _split_doc(doc: str):
        cur_directive = 'main'
        parsed = {
            cur_directive: []
        }

        if not doc:
            return {
                **parsed,
                "Args": _ARGS,
                "Hint": [_HINT]
            }

        directives = ['Args:', 'Hint:', 'Warnings:', 'Note:']

        in_args = False
        cur_directive = 'main'
        parsed = {
            cur_directive: []
        }
        last_arg = ''

        for line in doc.splitlines():
            if (striped_line := line.strip()) in directives:
                cur_directive = striped_line[:-1]

                if cur_directive == 'Args':
                    in_args = True
                    parsed[cur_directive] = {}

                else:
                    in_args = False
                    parsed[cur_directive] = []

                continue

            if in_args:
                if striped_line:
                    k, _, v = striped_line.partition(':')
                    if _:
                        parsed[cur_directive][k.strip()] = v.strip()
                        last_arg = k
                    else:
                        parsed[cur_directive][last_arg] += striped_line.strip()
            else:
                parsed[cur_directive].append(line)

        args = parsed.pop('Args', {})
        hint = parsed.pop('Hint', [])
        parsed['Args'] = {**_ARGS, **args}

        hint.append(_HINT)
        parsed['Hint'] = hint

        return parsed

    @staticmethod
    def _recover_doc(doc_dict: Dict):
        doc: List[str] = doc_dict.pop('main')
        doc.append('\n')
        args: Dict[str, str] = doc_dict.pop('Args')

        doc.append('Args:')
        doc.extend(f"    {k}: {v}" for k, v in args.items())
        doc.append('\n')

        for k, v in doc_dict.items():
            doc.append(k + ":")
            doc.extend(v)
            doc.append('\n')

        return '\n'.join(doc)


class ElementBase(metaclass=_AppendDoc):
    """deepfos平台元素的基类"""

    #: 元素绑定的api类
    api_class: Type[DynamicRootAPI] = None
    #: 元素对应的组件API
    api = None
    #: 元素类型
    element_type: str = None
    #: 元素的基础信息
    element_info: ModuleServerNameVO

    def __init__(
        self,
        element_name: str,
        folder_id: str = None,
        path: str = None,
        server_name: str = None,
    ):
        self.element_name = element_name
        self._folder_id = folder_id
        self._path = path
        self.element_info = None  # noqa

        if (
            OPTION.boost.skip_internal_existence_check
            and folder_id is not None
            and server_name is not None
            and (match := RE_SERVER_NAME_PARSER.match(server_name))
        ):
            self.element_info = ele_detail = ModuleServerNameVO(
                elementName=element_name,
                elementType=self.element_type,
                folderId=folder_id,
                serverName=server_name,
                moduleVersion=match.group('ver').replace('-', '.')
            )
        else:
            ele_detail = self._init_element()

        if self.api_class:
            self._init_api(ele_detail)

    def _init_element(self) -> ModuleServerNameVO:
        """初始化元素"""
        ele_info = self._get_element_info()
        self.element_info = ModuleServerNameVO.construct_from(ele_info)
        return ele_info

    def _init_api(self, ele_info: ModuleServerNameVO) -> None:
        """初始化API"""
        self.api = api = self.api_class(version=self._get_version(ele_info), lazy=True)
        api.set_url(ele_info.serverName)
        self._update_api_cache(api, ele_info)

    @staticmethod
    def _get_version(ele_info):
        """

        Returns: version_id with format as '1_0' or None if no version_id got

        """
        if match := RE_SERVER_NAME_PARSER.match(ele_info.serverName):
            return match.group('ver').replace('-', '_')

        # Init with path or folderId provided
        if isinstance(ele_info, ModuleServerNameVO):
            # Format example: "2.0"
            if ele_info.moduleVersion:
                return ele_info.moduleVersion.replace('.', '_')
        else:
            # Format example: "MAINVIEW1_0"
            if ele_info.moduleId and (match := RE_MODULEID_PARSER.match(ele_info.moduleId)):
                return match.group('ver')
            # Format example: "2.0"
            if ele_info.moduleVersion:
                return ele_info.moduleVersion.replace('.', '_')

    @classmethod
    def _update_api_cache(cls, api, ele_info):
        if isinstance(ele_info, ElementRelationInfo):
            # 更新api_class的缓存
            api.__class__.server_cache[ele_info.moduleId] = \
                ele_info.serverName
            api.module_id = ele_info.moduleId
        else:
            api.module_id = f"{api.module_type}{cls._get_version(ele_info)}"

    def _get_element_info(self) -> T_ElementInfoWithServer:
        """获取元素信息"""
        ele_name, path, folder = \
            self.element_name, self._path, self._folder_id

        return self.check_exist(
            ele_name, self._get_element_type(),
            folder=folder, path=path, silent=False)

    @classmethod
    def _get_element_type(cls):
        if cls.element_type is None and cls.api_class is None:
            raise ElementTypeMissingError(
                "Either api_class or module_type should be provided.")

        return cls.element_type or cls.api_class.module_type

    @classmethod
    def check_exist(
        cls,
        ele_name: str,
        ele_type: str = None,
        folder: str = None,
        path: str = None,
        silent: bool = True,
    ) -> Union[T_ElementInfoWithServer, int]:
        """查询元素是否存在

        Args:
            ele_name: 元素名
            ele_type: 元素类型
            folder: 文件夹id
            path: 文件夹路径
            silent: 元素不唯一是是否报错

        Returns:
            - 当指定 ``silent`` 为 ``True`` 时，返回查询到的元素个数（ :obj:`int` 类型）。
            - 当指定 ``silent`` 为 ``False`` 时，如果元素个数唯一，返回该元素
              （ :class:`ModuleServerNameVO` 或 :class:`ElementRelationInfo` 类型），否则将报错。

        """
        if ele_type is None:
            ele_type = cls._get_element_type()

        api = AppAPI(sync=True)

        if path is None and folder is None:
            ele_list = api.elements.get_element_info_by_name(ele_name, ele_type)
        else:
            ele_list = api.element_info.get_server_names([ElementModel(
                elementName=ele_name, elementType=ele_type,
                folderId=folder, path=path
            )])

        ele_no = len(ele_list or [])
        if silent:
            return ele_no

        if ele_no == 0:
            raise ElementNotFoundError(
                f"element name: {ele_name}, element type: {ele_type}.")
        elif ele_no > 1:
            raise ElementAmbiguousError(
                f"Found {ele_no} elements for element name: {ele_name}, "
                f"element type: {ele_type}.")

        return ele_list[0]


# noinspection PyMissingConstructor,PyUnresolvedReferences
class AsyncElementBase(ElementBase):
    def __init__(
        self,
        element_name: str,
        folder_id: str = None,
        path: str = None,
        server_name: str = None,
    ):
        self.element_name = element_name
        self._folder_id = folder_id
        self._path = path
        # noinspection PyTypeChecker
        #: 元素的基础信息
        self.element_info: ModuleServerNameVO = None
        self._initialized = False
        self._server_name = server_name

    def __await__(self):
        return self._init_element().__await__()

    async def _init_element(self):
        """初始化元素"""
        if (
            OPTION.boost.skip_internal_existence_check
            and self._folder_id is not None
            and self._server_name is not None
            and (match := RE_SERVER_NAME_PARSER.match(server_name))
        ):
            self.element_info = ele_info = ModuleServerNameVO(
                elementName=self.element_name,
                elementType=self.element_type,
                folderId=self._folder_id,
                serverName=self._server_name,
                moduleVersion=match.group('ver').replace('-', '.')
            )
        else:
            ele_info = await self._get_element_info()
            self.element_info = ModuleServerNameVO.construct_from(ele_info)

        if self.api_class:
            await self._init_api(ele_info)

        self._initialized = True
        return self

    async def _init_api(self, ele_info: T_ElementInfoWithServer) -> None:
        self.api = api = await self.api_class(sync=False, version=self._get_version(ele_info), lazy=True)
        self._update_api_cache(api, ele_info)

    async def _get_element_info(self) -> T_ElementInfoWithServer:
        """获取元素信息"""
        ele_name, path, folder = \
            self.element_name, self._path, self._folder_id

        return await self.check_exist(
            ele_name, self._get_element_type(),
            folder=folder, path=path, silent=False)

    @classmethod
    async def check_exist(
        cls,
        ele_name: str,
        ele_type: str = None,
        folder: str = None,
        path: str = None,
        silent: bool = True,
    ) -> Union[T_ElementInfoWithServer, int]:
        if ele_type is None:
            ele_type = cls._get_element_type()

        api = AppAPI(sync=False)

        if path is None and folder is None:
            ele_list = await api.elements.get_element_info_by_name(ele_name, ele_type)
        else:
            ele_list = await api.element_info.get_server_names([ElementModel(
                elementName=ele_name, elementType=ele_type,
                folderId=folder, path=path
            )])

        ele_no = len(ele_list or [])
        if silent:
            return ele_no

        if ele_no == 0:
            raise ElementNotFoundError(
                f"element name: {ele_name}, element type: {ele_type}.")
        elif ele_no > 1:
            raise ElementAmbiguousError(
                f"Found {ele_no} elements for element name: {ele_name}, "
                f"element type: {ele_type}.")

        return ele_list[0]

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)

        if item == '_initialized':
            return attr

        if self._initialized or \
                (item.startswith('__') and item.endswith('__')) or \
                item in AsyncElementBase.__dict__ or \
                not inspect.iscoroutinefunction(attr):
            return attr

        @functools.wraps(attr)
        async def wrapped(*args, **kwargs):
            if not self._initialized:
                await self._init_element()

            return await attr(*args, **kwargs)

        return wrapped
