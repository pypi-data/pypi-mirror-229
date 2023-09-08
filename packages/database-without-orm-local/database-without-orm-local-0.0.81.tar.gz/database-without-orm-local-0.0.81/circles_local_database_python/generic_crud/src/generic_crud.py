from circles_local_database_python.connector import Connector
from typing import Any, Union, List
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'circles_local_database_python')
sys.path.append(src_path)
DATABASE_WITHOUT_ORM_PYTHON_PACKAGE_COMPONENT_ID = 13
DATABASE_WITHOUT_ORM_PYTHON_PACKAGE_COMPONENT_NAME = 'circles_local_database_python\\generic_crud'
DEVELOPER_EMAIL = 'sahar.g@circ.zone'
obj = {
    'component_id': DATABASE_WITHOUT_ORM_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': DATABASE_WITHOUT_ORM_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}
logger = Logger.create_logger(object=obj)


class GenericCRUD:

    def __init__(self):
        pass

    def _serialize_datetime(result):
        result_serializable = []
        for row in result:
            row_serializable = list(row)
            for i, value in enumerate(row_serializable):
                if isinstance(value, datetime):
                    row_serializable[i] = value.strftime('%Y-%m-%d %H:%M:%S')
            result_serializable.append(tuple(row_serializable))
        return result_serializable

    def _validate_parameters(parameters):
        for param in parameters:
            if not param:
                raise ValueError(f"{param} cannot be empty")


    @staticmethod
    # TODO: Add optional parameter of select_clause_value: str
    def fetchall_by_id(schema_name: str, table_name: str, select_clause: Union[str, List[str]], id_column_name: str, id_column_value: int) -> Any:
        """
        This method gets the data from the database for the given table name and id.
        :param db_name: The name of the database
        :param table_name: The name of the table
        :param select_cluse: The select clause for the query
        :param id_col_name: The name of the id column in the table
        :param id_col_value: The value of the id column in the table
        :return: The data from the database for the given table name and id
        """
        obj = {
            'schema_name': schema_name,
            'table_name': table_name,
            'select_cluse': select_clause,
            'id': id_column_value,
            'id_col_name': id_column_name
        }
        logger.start(object=obj)
        # TODO: If have select_clause_value is empty assign "*"
        try:
            # Connect to the database
            connection = Connector.connect(schema_name=schema_name)
            cursor = connection.cursor()
        except Exception as e:
            message = "error: connection to the database failed"
            logger.exception(message, object=e)
            raise Exception(message)

        try:
            # Check parameters
            GenericCRUD._validate_parameters([schema_name, table_name, id_column_name, id_column_value])
            if isinstance(select_clause, List):
                select_clause = ','.join(select_clause)

            # Get the data from the database
            query = f"SELECT {select_clause} FROM {table_name} WHERE {id_column_name} = {id_column_value}"
            cursor.execute(query)

            # Get the result
            temp_result = cursor.fetchall()
            result = GenericCRUD._serialize_datetime(temp_result)
            # Return the result
            logger.end(object={'result': result})
            return result
        except Exception as e:
            message = "error: failed to get data from the database"
            logger.exception(message, object=e)
            logger.end(object={'message': message})
            raise Exception(message)

    @staticmethod
    def fetchall_by_where_condition(schema_name: str, table_name: str, select_clause: Union[str, List[str]] = "*", where_condition: str = "") -> Any:
        """
        This method gets the data from the database for the given table name.
        :param db_name: The name of the database
        :param table_name: The name of the table
        :param select_cluse: The select clause for the query (default: "*")
        :param where_cond: The where condition for the query (default: "")
        :return: The data from the database for the given table name and where the condition
        """
        obj = {
            'schema_name': schema_name,
            'table_name': table_name,
            'select_cluse': select_clause,
            'where_condition': where_condition
        }
        logger.start(object=obj)
        try:
            # Connect to the database
            connection = Connector.connect(schema_name=schema_name)
            cursor = connection.cursor()
        except Exception as e:
            # If the connection fails, write an error message to the log
            message = "error: connection to the database failed"
            logger.exception(message, object=e)
            logger.end(object={'message': message})
            raise Exception(message)
        try:
            # Check parameters
            # TODO: if environment.check_parameters() { if !validate_select_database_object_name( database_object_name: str) ->
            # bool message="Database object do not end with _view" logger.end() raise ValueError(message) }
            GenericCRUD._validate_parameters([schema_name, table_name])

            query = ""
            if isinstance(select_clause, List):
                if not select_clause:  # Check if it's an empty list
                    select_clause = "*"  # Set it to the default "*"
                else:
                    select_clause = ','.join(select_clause)
            else:
                if not select_clause:  # Check if it's an empty string
                    select_clause = "*"  # Set it to the default "*"

            query = f"SELECT {select_clause} FROM {table_name} WHERE {where_condition}" if where_condition else f"SELECT {select_clause} FROM {table_name}"
            cursor.execute(query)
            result = cursor.fetchall()
            result = GenericCRUD._serialize_datetime(result)
            logger.end(object={'result': str(result)})
            return result
        except Exception as e:
            # If the database query fails, write an error message to the log
            message = "error: failed to get data from the database"
            logger.exception(message, object=e)
            logger.end()
            raise Exception(message)

    @staticmethod
    def insert(schema_name: str, table_name: str, json_data) -> Any:
        """
        This method inserts the data into the database for the given table name.
        :param db_name: The name of the database
        :param table_name: The name of the table
        :param json_data: The data to insert into the database (default: None)
        :return: The message and the ids of the inserted data
        """
        obj = {
            'schema_name': schema_name,
            'table_name': table_name,
            'json_data': json_data
        }
        logger.start(object=obj)
        try:
            connection = Connector.connect(schema_name=schema_name)
            cursor = connection.cursor()
        except Exception as e:
            message = "error: connection to the database failed"
            logger.exception(message, object=e)
            raise Exception(message + str(e))

        try:
            # Check parameters
            GenericCRUD._validate_parameters([schema_name, table_name, json_data])
            added_ids = []
            # Extract the data from the json
            keys = ','.join(json_data.keys())
            values = ['{}'.format(y) for y in json_data.values()]
            values = ','.join(values)
            query = f"INSERT INTO {table_name} ({keys}) VALUES ({values})"
            cursor.execute(query)
            added_ids.append(cursor.lastrowid())
            connection.commit()
            logger.end(
                object={'message': 'Contacts added successfully', 'contacts ids': added_ids})
            return {'message': 'Contacts added successfully', 'contacts ids': added_ids}

        except Exception as e:
            message = "error: failed to insert data into the database "
            logger.exception(message, object=e)
            logger.end(object={'message': message})
            raise Exception(message + str(e))

    @staticmethod
    def update(schema_name: str, table_name: str, data_json, id_column_name: str, id_column_value: int) -> Any:
        """
        This method updates the data in the database for the given table name.
        :param db_name: The name of the database
        :param table_name: The name of the table
        :param json_data: The data to update in the database
        :param id_col_name: The name of the id column in the table
        :return: The message and the ids of the updated data
        """
        obj = {
            'schema_name': schema_name,
            'table_name': table_name,
            'data_json': data_json,
            'id_column_name': id_column_name,
            'id_column_value': id_column_value
        }

        logger.start(object=obj)
        try:
            connection = Connector.connect(schema_name=schema_name)
            cursor = connection.cursor()
        except Exception as e:
            message = "error: connection to the database failed"
            logger.exception(message, object=e)
            return {'message': message}

        try:
            # Check parameters
            GenericCRUD._validate_parameters([schema_name, table_name, id_column_name, id_column_value])
            updated_ids = []
            # Extract the data from the json
            set_clause = ', '.join(
                [f"{key} = '{value}'" for key, value in data_json.items()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column_name} = {id_column_value}"
            cursor.execute(query)
            updated_ids.append(cursor.lastrowid())
            connection.commit()
            obj = {'updated_ids': updated_ids}
            logger.end('updated successfully', object=obj)
            return {'message': 'Contacts updated successfully', 'contacts ids': updated_ids}
        except Exception as e:
            message = "error: failed to update data in the database"
            logger.exception(message, object=e)
            logger.end(message)
            raise Exception(message)

    @staticmethod
    def update_by_where_condition(schema_name: str, table_name: str, data_json, where_condition: str) -> Any:
        """
        This method updates the data in the database for the given table name.
        :param db_name: The name of the database
        :param table_name: The name of the table
        :param json_data: The data to update in the database
        :param where_condition: The where condition for the query (no need to add the WHERE keyword)
        :return: The message and the ids of the updated data
        """
        obj = {
            'schema_name': schema_name,
            'table_name': table_name,
            'data_json': data_json,
            'where_condition': where_condition
        }
        logger.start(object=obj)
        try:
            connection = Connector.connect(schema_name=schema_name)
            cursor = connection.cursor()
        except Exception as e:
            message = "error: connection to the database failed"
            logger.exception(message, object=e)
            raise Exception(message + str(e))

        try:
            # TODO: if environment.check_parameters() { if !validate_none_select_database_object_name( database_object_name: str)
            # Check parameters
            GenericCRUD._validate_parameters([schema_name, table_name, where_condition])
            updated_ids = []
            # Extract the data from the json
            set_clause = ', '.join(
                [f"{key} = '{value}'" for key, value in data_json.items()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_condition}"
            print(query)
            cursor.execute(query)
            updated_ids.append(cursor.lastrowid())
            connection.commit()
            obj = {'updated_ids': updated_ids}
            logger.end('updated successfully', object=obj)
            return {'message': 'Contacts updated successfully', 'contacts ids': updated_ids}
        except Exception as e:
            message = "error: failed to update data in the database"
            logger.exception(message, object=e)
            logger.end(message)
            raise Exception(message + str(e))

    @staticmethod
    def delete(schema_name: str, table_name: str, data_json, id_column_name: str, id_column_value: int) -> None:
        """
        This method deletes the data from the database for the given table name.
        :param db_name: The name of the database
        :param table_name: The name of the table
        :param json_data: The data to delete from the database
        :param id_col_name: The name of the id column in the table (default: id)
        :return: The message and the ids of the deleted data
        """
        obj = {
            'schema_name': schema_name,
            'table_name': table_name,
            'data_json': data_json,
            'id_column_name': id_column_name,
            'id_column_value': id_column_value
        }
        logger.start(object=obj)
        try:
            connection = Connector.connect(schema_name=schema_name)
            cursor = connection.cursor()
        except Exception as e:
            message = "error: connection to the database failed"
            logger.exception(message, object=e)
            logger.end(message)
            raise Exception(message + str(e))
        try:
            # Check parameters
            GenericCRUD._validate_parameters([schema_name, table_name, id_column_name, id_column_value])

            deleted_ids = []
            query = f"UPDATE {table_name} SET end_timestamp = NOW() WHERE {id_column_name} = {id_column_value};"
            cursor.execute(query)
            deleted_ids.append(cursor.lastrowid())
            connection.commit()
            logger.end('Deleted successfully', object={
                       'contacts ids': deleted_ids})
            return {'message': 'Deleted successfully', 'contacts ids': deleted_ids}
        except Exception as e:
            message = "error: failed to delete data from the database"
            logger.exception(message, object=e)
            logger.end(message)
            raise Exception(message + str(e))

    @staticmethod
    def delete_by_where_condition(schema_name: str, table_name: str, where_condition: str) -> None:
        """
        This method deletes the data from the database for the given table name.
        :param db_name: The name of the database
        :param table_name: The name of the table
        :param where_condition: The where condition for the query (no need to add the WHERE keyword)
        :return: The message and the ids of the deleted data
        """
        obj = {
            'schema_name': schema_name,
            'table_name': table_name,
            'where_condition': where_condition
        }
        logger.start(object=obj)
        try:
            connection = Connector.connect(schema_name=schema_name)
            cursor = connection.cursor()
        except Exception as e:
            message = "error: connection to the database failed"
            logger.exception(message, object=e)
            logger.end(message)
            raise Exception(message + str(e))

        try:
            # Check parameters
            GenericCRUD._validate_parameters([schema_name, table_name, where_condition])
            deleted_ids = []
            query = f"UPDATE {table_name} SET end_timestamp = NOW() WHERE {where_condition};"
            cursor.execute(query)
            deleted_ids.append(cursor.lastrowid())
            connection.commit()
            logger.end('Deleted successfully', object={
                       'contacts ids': deleted_ids})
            return {'message': 'Deleted successfully', 'contacts ids': deleted_ids}
        except Exception as e:
            message = "error: failed to delete data from the database"
            logger.exception(message, object=e)
            logger.end(message)
            raise Exception(message + str(e))
