
import snowflake
from typing import List

from dftools.core.database import ConnectionWrapper

from dftools_snowflake.connection.snowflake_connection_info import SnowflakeConnectionInfo, SnowflakeConnectionSchemaInfo

class SnowflakeConnectionWrapper(ConnectionWrapper):

    def __init__(self, connection_info : SnowflakeConnectionInfo, schema_info : SnowflakeConnectionSchemaInfo = None) -> None:
        """
        Creates a new connection wrapper for Snowflake, storing the current connection information state and initialises the connection

        Parameters
        -----------
            connectionInfo: The snowflake connection information. This parameter is mandatory
            schemaInfo : The snowflake schema information
        """
        self.connection_info = connection_info
        self.conn = connection_info.create_new_connection()
        self.set_snowflake_connection_schema_info(schema_info)

    def set_snowflake_connection_schema_info(self, schema_info : SnowflakeConnectionSchemaInfo) -> None:
        """
        Sets the Snowflake Connection Schema Information object and updates the connection current connection schema information.

        Parameters
        -----------
            schemaInfo : The snowflake schema information to apply on connection
        """
        self.schema_info = schema_info
        if self.schema_info is not None :
            self.update_connection_schema_info()

    # Connection methods
    def get_current_catalog(self) -> str:
        return self.get_schema_info().db
    
    def get_current_namespace(self) -> str:
        return self.get_schema_info().schema
    
    def close_connection(self):
        return self.conn.close()
    
    # Snowflake specific methods

    def get_cursor(self):
        """
        Sets the Snowflake Connection Schema Information object and updates the connection current connection schema information.

        Returns
        -----------
            cursor : A cursor on the current connection stored in this wrapper
        """
        return self.conn.cursor()

    def get_schema_info(self) -> SnowflakeConnectionSchemaInfo:
        """
        Get the Snowflake Connection Schema Information object

        Returns
        -----------
            snowflake_connection_schema_info : The Snowflake Connection Schema Information
        """
        return self.schema_info
    
    def has_schema_info(self) -> SnowflakeConnectionSchemaInfo:
        """
        Checks if the Snowflake Connection Schema Information object is available

        Returns
        -----------
            True if schema information is available, False otherwise
        """
        return self.schema_info is not None

    def get_schema(self):
        """
        Get the Schema object

        Returns
        -----------
            schema_info : The Schema
        """
        return self.get_schema_info().schema if self.has_schema_info() else None
    
    def has_schema(self):
        """
        Checks if schema is available on this connection

        Returns
        -----------
            True if schema is available, False otherwise
        """
        return self.get_schema() is not None

    def update_connection_schema_info(self):
        """
        Update the connection schema information stored in this wrapper and updates the connection.
        """
        cur = self.get_cursor()
        if self.schema_info.role is None :
            cur.close()
            return

        try:
            cur.execute(f"USE ROLE {self.schema_info.role}")
        except snowflake.connector.errors.ProgrammingError as e:
            print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
            raise RuntimeError("Role " + self.schema_info.role + " cannot be set")
        
        if self.schema_info.warehouse is not None :
            try:
                cur.execute(f"USE WAREHOUSE {self.schema_info.warehouse}")
            except snowflake.connector.errors.ProgrammingError as e:
                print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
                raise RuntimeError("Warehouse " + self.schema_info.warehouse + " cannot be set")

        if self.schema_info.db is not None :
            try:
                cur.execute(f"USE DATABASE {self.schema_info.db}")
            except snowflake.connector.errors.ProgrammingError as e:
                print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
                raise RuntimeError("Database " + self.schema_info.db + " cannot be set")
        else :
            cur.close()
            return

        try:
            cur.execute(f"USE SCHEMA {self.schema_info.schema}")
        except snowflake.connector.errors.ProgrammingError as e:
            print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
            raise RuntimeError("Schema " + self.schema_info.schema + " cannot be set")
        
        cur.close()
    
    # Query and script execution methods

    def execute_query(self, query : str) -> list:
        """
        Executes a query on the snowflake connection contained in the wrapper.
        An error is raised on any ProgrammingError encountered

        Parameters
        -----------
            query : The query to execute
        
        Returns
        -----------
            result_set_list : The list of result set, or None if query encountered an error
        """
        cur = self.get_cursor()
        try:
            cur.execute(query)
            return list(cur)
        except snowflake.connector.errors.ProgrammingError as e:
            print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
            raise e
        finally:
            cur.close()

    def execute_queries(self, query_list : List[str]) -> None:
        """
        Executes a list of queries on the snowflake connection contained in the wrapper.
        An error is raised on any ProgrammingError encountered

        Parameters
        -----------
            query_list : The list of queries to execute
        
        Returns
        -----------
            result_set_list : The list of result set, or None if query encountered an error
        """
        result_set_list = []
        cur = self.get_cursor()
        for query in query_list:
            try:
                cur.execute(query)
                result_set = cur.fetchall()
                if result_set is not None :
                    result_set_list.append(result_set)
            except snowflake.connector.errors.ProgrammingError as e:
                print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
                result_set_list.append(['Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid)])
                return result_set_list
        cur.close()
        return result_set_list

    def write_result_set_to_file(file_path, result_set) -> None:
        """
        Writes a result set to a local file

        Parameters
        -----------
            file_path : str
                The target file name path
            result_set : str
                The result set
        """
        with open(file_path, "w") as outputFile:
            for (data) in result_set[0]:
                outputFile.write(data)


    def write_dict_to_file(file_path, in_dict : dict) -> None:
        """
        Writes an input dictionnary to a local file

        Parameters
        -----------
            file_path : str
                The target file name path
            in_dict : str
                The input dictionnary
        """
        with open(file_path, "w") as outputFile:
            for (data) in in_dict:
                outputFile.write(data)
                
    def write_query_result_to_file(self, query: str, target_file_path : str) -> list:
        """
        Executes a query on the snowflake connection contained in the wrapper and creates a file with the result

        Parameters
        -----------
            query : str
                The query to execute
            target_file_path : str
                The target file name path
        """
        self.write_result_set_to_file(file_path=target_file_path, result_set=self.execute_query(query))
