from deepfos.lazy_import import lazy_callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cube import SysCube, Cube, as_function_node
    from .dimension import DimMember, SysDimension, read_expr, Dimension, DimExprAnalysor, ElementDimension
    from .logictable import SQLCondition, BaseTable, MetaTable, TreeRenderer

SysCube, Cube, as_function_node = lazy_callable('deepfos.core.cube',  # noqa
                                                'SysCube',
                                                'Cube',
                                                'as_function_node')

(DimMember, SysDimension, read_expr,  # noqa
 Dimension, DimExprAnalysor, ElementDimension) = lazy_callable('deepfos.core.dimension',  # noqa
                                                               'DimMember',
                                                               'SysDimension',
                                                               'read_expr',
                                                               'Dimension',
                                                               'DimExprAnalysor',
                                                               'ElementDimension')

SQLCondition, BaseTable, MetaTable, TreeRenderer = lazy_callable('deepfos.core.logictable',  # noqa
                                                                 'SQLCondition',
                                                                 'BaseTable',
                                                                 'MetaTable',
                                                                 'TreeRenderer')
