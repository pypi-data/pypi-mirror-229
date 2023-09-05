from deepfos.lazy_import import lazy_callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .accounting import AccountingEngines, BillEngines, CallbackInfo
    from .apvlprocess import ApprovalProcess
    from .bizmodel import BusinessModel, CopyConfig
    from .datatable import (
        Datatable,
        DataTableMySQL,
        DataTableClickHouse,
        DataTableOracle,
        DataTableSQLServer,
        DataTableGauss,
        DataTableKingBase,
        DataTableDaMeng,
        DataTablePostgreSQL,
        DataTableDeepEngine,
    )
    from .dimension import AsyncDimension, Dimension, Strategy
    from .fact_table import FactTable
    from .finmodel import FinancialCube
    from .journal_template import JournalTemplate, FullPostingParameter
    from .rolestrategy import RoleStrategy
    from .smartlist import SmartList
    from .variable import Variable
    from .workflow import WorkFlow
    from .reconciliation import ReconciliationEngine, ReconciliationMsEngine


AccountingEngines, BillEngines, CallbackInfo = lazy_callable( # noqa
    'deepfos.element.accounting',
    'AccountingEngines', 'BillEngines', 'CallbackInfo'
)
ApprovalProcess, = lazy_callable(  # noqa
    'deepfos.element.apvlprocess',
    'ApprovalProcess'
)
BusinessModel, CopyConfig = lazy_callable(  # noqa
    'deepfos.element.bizmodel',
    'BusinessModel', 'CopyConfig'
)
(
    Datatable,  # noqa
    DataTableMySQL,  # noqa
    DataTableClickHouse,  # noqa
    DataTableOracle,  # noqa
    DataTableSQLServer,  # noqa
    DataTableGauss,  # noqa
    DataTableKingBase,  # noqa
    DataTableDaMeng,  # noqa
    DataTablePostgreSQL,  # noqa
    DataTableDeepEngine,  # noqa
) = lazy_callable(  # noqa
    'deepfos.element.datatable',
    'Datatable',
    'DataTableMySQL',
    'DataTableClickHouse',
    'DataTableOracle',
    'DataTableSQLServer',
    'DataTableGauss',
    'DataTableKingBase',
    'DataTableDaMeng',
    'DataTablePostgreSQL',
    'DataTableDeepEngine',
)
AsyncDimension, Dimension, Strategy = lazy_callable(  # noqa
    'deepfos.element.dimension',
    'AsyncDimension', 'Dimension', 'Strategy'
)
FactTable, = lazy_callable('deepfos.element.fact_table', 'FactTable')  # noqa
FinancialCube, = lazy_callable('deepfos.element.finmodel', 'FinancialCube')  # noqa
JournalTemplate, FullPostingParameter = lazy_callable(  # noqa
    'deepfos.element.journal_template',
    'JournalTemplate', 'FullPostingParameter'
)
RoleStrategy, = lazy_callable('deepfos.element.rolestrategy', 'RoleStrategy')  # noqa
SmartList, = lazy_callable('deepfos.element.smartlist', 'SmartList')  # noqa
Variable, = lazy_callable('deepfos.element.variable', 'Variable')  # noqa
WorkFlow, = lazy_callable('deepfos.element.workflow', 'WorkFlow')  # noqa
ReconciliationEngine, ReconciliationMsEngine = lazy_callable(  # noqa
    'deepfos.element.reconciliation',
    'ReconciliationEngine', 'ReconciliationMsEngine'
)
