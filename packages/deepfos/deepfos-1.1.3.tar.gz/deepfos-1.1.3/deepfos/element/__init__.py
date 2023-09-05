from deepfos.lazy_import import lazy_callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .accounting import (
        AccountingEngines, AsyncAccountingEngines, BillEngines, AsyncBillEngines, CallbackInfo
    )
    from .apvlprocess import AsyncApprovalProcess, ApprovalProcess
    from .bizmodel import BusinessModel, AsyncBusinessModel, CopyConfig
    from .datatable import (Datatable,
                            AsyncDataTableMySQL, DataTableMySQL,
                            AsyncDataTableClickHouse, DataTableClickHouse,
                            AsyncDataTableOracle, DataTableOracle,
                            AsyncDataTableSQLServer, DataTableSQLServer,
                            AsyncDataTableKingBase, DataTableKingBase,
                            AsyncDataTableGauss, DataTableGauss,
                            AsyncDataTableDaMeng, DataTableDaMeng,
                            AsyncDataTablePostgreSQL, DataTablePostgreSQL,
                            AsyncDataTableDeepEngine, DataTableDeepEngine,
                            )
    from .dimension import AsyncDimension, Dimension
    from .fact_table import AsyncFactTable, FactTable
    from .finmodel import AsyncFinancialCube, FinancialCube
    from .journal_template import AsyncJournalTemplate, JournalTemplate, FullPostingParameter
    from .rolestrategy import AsyncRoleStrategy, RoleStrategy
    from .smartlist import AsyncSmartList, SmartList
    from .variable import AsyncVariable, Variable
    from .workflow import AsyncWorkFlow, WorkFlow

(
    AccountingEngines, AsyncAccountingEngines, BillEngines, AsyncBillEngines, CallbackInfo  # noqa
) = lazy_callable(
    'deepfos.element.accounting',
    'AccountingEngines', 'AsyncAccountingEngines', 'BillEngines', 'AsyncBillEngines', 'CallbackInfo'
)

AsyncApprovalProcess, ApprovalProcess = lazy_callable('deepfos.element.apvlprocess',  # noqa
                                                      'AsyncApprovalProcess', 'ApprovalProcess')

BusinessModel, AsyncBusinessModel, CopyConfig = lazy_callable('deepfos.element.bizmodel',  # noqa
                                                              'BusinessModel', 'AsyncBusinessModel', 'CopyConfig')

(
    Datatable,  # noqa
    AsyncDataTableMySQL, DataTableMySQL,  # noqa
    AsyncDataTableClickHouse, DataTableClickHouse,  # noqa
    AsyncDataTableOracle, DataTableOracle,  # noqa
    AsyncDataTableSQLServer, DataTableSQLServer,  # noqa
    AsyncDataTableKingBase, DataTableKingBase,  # noqa
    AsyncDataTableGauss, DataTableGauss,  # noqa
    AsyncDataTableDaMeng, DataTableDaMeng,  # noqa
    AsyncDataTablePostgreSQL, DataTablePostgreSQL,  # noqa
    AsyncDataTableDeepEngine, DataTableDeepEngine,  # noqa
) = lazy_callable(  # noqa
    'deepfos.element.datatable',
    'Datatable',
    'AsyncDataTableMySQL', 'DataTableMySQL',
    'AsyncDataTableClickHouse', 'DataTableClickHouse',
    'AsyncDataTableOracle', 'DataTableOracle',
    'AsyncDataTableSQLServer', 'DataTableSQLServer',
    'AsyncDataTableKingBase', 'DataTableKingBase',
    'AsyncDataTableGauss', 'DataTableGauss',
    'AsyncDataTableDaMeng', 'DataTableDaMeng',
    'AsyncDataTablePostgreSQL', 'DataTablePostgreSQL',
    'AsyncDataTableDeepEngine', 'DataTableDeepEngine',
)

AsyncDimension, Dimension = lazy_callable('deepfos.element.dimension',  # noqa
                                          'AsyncDimension', 'Dimension')

AsyncFactTable, FactTable = lazy_callable('deepfos.element.fact_table',  # noqa
                                          'AsyncFactTable', 'FactTable')

AsyncFinancialCube, FinancialCube = lazy_callable('deepfos.element.finmodel',  # noqa
                                                  'AsyncFinancialCube', 'FinancialCube')

AsyncJournalTemplate, JournalTemplate, FullPostingParameter = lazy_callable(  # noqa
    'deepfos.element.journal_template',
    'AsyncJournalTemplate', 'JournalTemplate', 'FullPostingParameter')

AsyncRoleStrategy, RoleStrategy = lazy_callable('deepfos.element.rolestrategy',  # noqa
                                                'AsyncRoleStrategy', 'RoleStrategy')

AsyncSmartList, SmartList = lazy_callable('deepfos.element.smartlist',  # noqa
                                          'AsyncSmartList', 'SmartList')

AsyncVariable, Variable = lazy_callable('deepfos.element.variable',  # noqa
                                        'AsyncVariable', 'Variable')

AsyncWorkFlow, WorkFlow = lazy_callable('deepfos.element.workflow', 'AsyncWorkFlow', 'WorkFlow')  # noqa

AsyncReconciliationEngine, AsyncReconciliationMsEngine, ReconciliationEngine, ReconciliationMsEngine = lazy_callable(  # noqa
    'deepfos.element.reconciliation',
    'AsyncReconciliationEngine', 'AsyncReconciliationMsEngine',
    'ReconciliationEngine', 'ReconciliationMsEngine',
)
