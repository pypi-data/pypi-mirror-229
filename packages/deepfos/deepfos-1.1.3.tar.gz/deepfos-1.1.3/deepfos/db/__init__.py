from deepfos.lazy_import import lazy_callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .mysql import MySQLClient, AsyncMySQLClient
    from .clickhouse import ClickHouseClient, AsyncClickHouseClient
    from .oracle import OracleClient, AsyncOracleClient, OracleDFSQLConvertor
    from .sqlserver import SQLServerClient, AsyncSQLServerClient
    from .kingbase import KingBaseClient, AsyncKingBaseClient
    from .gauss import GaussClient, AsyncGaussClient
    from .dameng import DaMengClient, AsyncDaMengClient
    from .postgresql import PostgreSQLClient, AsyncPostgreSQLClient
    from .deepengine import DeepEngineClient, AsyncDeepEngineClient

MySQLClient, AsyncMySQLClient = lazy_callable('deepfos.db.mysql',   # noqa
                                              'MySQLClient',
                                              'AsyncMySQLClient')

ClickHouseClient, AsyncClickHouseClient = lazy_callable('deepfos.db.clickhouse',    # noqa
                                                        'ClickHouseClient',
                                                        'AsyncClickHouseClient')

OracleClient, AsyncOracleClient, OracleDFSQLConvertor = lazy_callable('deepfos.db.oracle',  # noqa
                                                                      'OracleClient',
                                                                      'AsyncOracleClient',
                                                                      'OracleDFSQLConvertor')

SQLServerClient, AsyncSQLServerClient = lazy_callable('deepfos.db.sqlserver',   # noqa
                                                      'SQLServerClient',
                                                      'AsyncSQLServerClient')

KingBaseClient, AsyncKingBaseClient = lazy_callable('deepfos.db.kingbase',  # noqa
                                                      'KingBaseClient',
                                                      'AsyncKingBaseClient')

GaussClient, AsyncGaussClient = lazy_callable('deepfos.db.gauss',  # noqa
                                                      'GaussClient',
                                                      'AsyncGaussClient')

DaMengClient, AsyncDaMengClient = lazy_callable('deepfos.db.dameng',  # noqa
                                                      'DaMengClient',
                                                      'AsyncDaMengClient')

PostgreSQLClient, AsyncPostgreSQLClient = lazy_callable('deepfos.db.postgresql',  # noqa
                                                        'PostgreSQLClient',
                                                        'AsyncPostgreSQLClient')

DeepEngineClient, AsyncDeepEngineClient = lazy_callable('deepfos.db.deepengine',  # noqa
                                                        'DeepEngineClient',
                                                        'AsyncDeepEngineClient')
