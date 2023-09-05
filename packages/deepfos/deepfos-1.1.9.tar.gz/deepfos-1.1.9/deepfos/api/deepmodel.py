from typing import Union, Awaitable, List

from deepfos.lib.decorator import cached_property
from .base import DynamicRootAPI, ChildAPI, get
from .models.deepmodel import *


class ObjectAPI(ChildAPI):
    endpoint = '/object'

    @get('all/get')
    def get_all(self, ) -> Union[ObjectOperationParam, Awaitable[ObjectOperationParam]]:
        return {}

    @get('list')
    def list(self, ) -> Union[List[ObjectBasicDTO], Awaitable[List[ObjectBasicDTO]]]:
        return {}


class DeepModelAPI(DynamicRootAPI, builtin=True):
    module_type = 'MAINVIEW'
    default_version = (1, 0)
    multi_version = False
    cls_name = 'DeepModelAPI'
    module_name = 'deepfos.api.deepmodel'
    api_version = (1, 0)

    @cached_property
    def object(self) -> ObjectAPI:
        return ObjectAPI(self)
