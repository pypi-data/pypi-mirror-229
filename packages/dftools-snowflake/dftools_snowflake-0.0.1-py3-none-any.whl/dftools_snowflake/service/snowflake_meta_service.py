
from dftools.core.database import DatabaseMetadataService, ConnectionWrapper
from dftools.core.database.connection_wrapper import ConnectionWrapper
from dftools_snowflake.util.snowflake_system_queries import get_snow_structure_query_for_namespace, get_snow_structure_query_for_namespace_and_table
from dftools_snowflake.service.meta_decoder import SnowStructureDecoder

class SnowMetadataService(DatabaseMetadataService):
    def __init__(self, connection_wrapper: ConnectionWrapper) -> None:
        super().__init__(connection_wrapper, SnowStructureDecoder())
    
    def get_structure_from_database(self, namespace : str, table_name : str) -> list:
        data_structure_extract_query = get_snow_structure_query_for_namespace_and_table(namespace=namespace, table_name=table_name)
        self.conn_wrap.execute_query("SHOW PRIMARY KEYS;")
        self.conn_wrap.execute_query("CREATE OR REPLACE TEMPORARY TABLE DATA_STRUCTURE_PRIMARY_KEYS AS SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));")
        result_set = self.conn_wrap.execute_query(data_structure_extract_query)
        return result_set[0]