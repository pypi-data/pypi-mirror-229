# pylint: disable=too-many-arguments
import logging
from typing import Union, Any, Sequence, List

from network_connector import SSHConnector
from sqlalchemy import (
    MetaData,
    CursorResult,
    URL,
    Select,
    Insert,
    Delete,
    Table,
    create_engine,
    inspect,
    func,
    select,
    insert,
    delete,
    text,
    exc,
)

from sql_repository.utils import assert_where_clause_have_all_parameters, assert_is_aggregate_function_with_where_clause

logging.basicConfig(
    level=logging.INFO,
    filename="./logging/logger.log",
    filemode='w',
    format='%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s',
)
logger = logging.getLogger(__name__)


class SQLRepository:
    def __init__(
        self,
        db_name: str,
        db_user: str,
        db_password: Union[str, int, None],
        db_host: str,
        db_port: int,
        db_schema: str = "public",
        dialect: str = "postgresql",
        connector: Union[SSHConnector, None] = None,
    ) -> None:
        """
        :param db_name: (str) Database name.
        :param db_user: (str) Database username.
        :param db_password: (Union[str, int, None]) Database password.
        :param db_host: (str) Database  username.
        :param db_port: (int) Database port.
        :param db_schema: (str) Database schema ("public", "mySchema", etc.). By defaut, use the  ``"public"``
            database schema.
        :param dialect: (str) Dialect used (ex. postgresql, mysql, mariadb, oracle, mssql, sqlite, etc.). By default,
            use the ``"postgresql"`` dialect.
        :param connector: Either or not to use a SSHConnector interface. By default, set to None for no connector.
        """

        db_port = db_port if connector is None else connector.ssh_local_bind_port

        self.url = URL.create(
            dialect, host=db_host, database=db_name, username=db_user, password=db_password, port=db_port
        )
        self._connect()

        self.engine = self.engine.connect()

        self.metadata = MetaData(schema=db_schema)
        self.metadata.reflect(self.engine)

        self.schema = inspect(self.engine)

        self._string_to_sqlalchemy_agg_func_mapping = {
            'max': func.max,
            'min': func.min,
            'count': func.count,
            'sum': func.sum,
            'rank': func.rank,
            'concat': func.concat,
        }

    def _connect(self) -> None:
        """
        Private method to connect to the database.
        """
        try:
            engine = create_engine(self.url)

            logger.info('Success - Database connected')
        except exc.SQLAlchemyError as error:
            logger.critical('Database connexion logging %s', error)
            raise error

        self.engine = engine

    def insert(self, table_name: str, data: List[dict]) -> None:
        """
        Perform a SQL insert statement.

        :param table_name: (str) Database table name.
        :param data: (List[dict]) data to be inserted.
        """

        table_obj = self.get_table_object(table_name)
        column_names = self.get_column_names(table_obj)
        values = self._order_data(column_names, data)

        query = insert(table_obj).values(values)

        self.engine.execute(query)
        self.engine.commit()

    def select(
        self,
        table_name: str,
        column_names: Union[List[str], None] = None,
        agg_fct: Union[str, None] = None,
        where_column_name: Union[str, None] = None,
        where_operator: Union[str, None] = None,
        where_value: Union[int, str, list, None] = None,
        execute_query: bool = True,
    ) -> Union[Sequence, Select]:
        """
        Perform SQL select statement.
        Example to select all columns where "col1" < 15:  select("table_example", None, "col1", "<", 15)
        Example to select all columns where  15 "col1" 20:  select("table_example", None, "col1", "between", [15, 20])
        Example to select column "col1" where "col2" in {1,2,3}:  select("table_example", "col1", "col2", "in", [1,2,3])

        :param table_name: (str) Database table name.
        :param column_names: (Union[List[str], None]) Columns to be selected, if None, no columns are select.
            By default, set to ``None``.
        :param agg_fct: (Union[str, None]) Either or not to use an aggregate SQL functions (ex. max, min, avg, etc.).
            By default, set to ``None`` for "don't use any".
        :param where_column_name: (Union[str, None]) Either or not to use a 'where' column name.
        By default, set to ``'None'``.
        :param where_operator: (Union[str, None]) Either or not to use an SQL operator (ex. >, <=, ==, in, between).
        By default, set to ``'None'``.
        :param where_value: (Union[int, str, list, None]) value(s) to be used in the 'where' clause.
        By default, set to ``'None'``.
        :param execute_query: (bool) If a query is to be executed or not. Use it to add new components to the query.
        By default, set to ``True``.

        :return: Data cursor or SQLAlchemy select query.
        """
        assert assert_where_clause_have_all_parameters(where_column_name, where_operator, where_value)
        assert assert_is_aggregate_function_with_where_clause(agg_fct, where_operator)

        table_obj = self.get_table_object(table_name)

        if agg_fct is None:
            column_names_to_use = self.get_column_names(table_obj) if column_names is None else column_names
            query_format = [table_obj.c[col] for col in column_names_to_use]
        else:
            sql_func = self._string_to_sqlalchemy_agg_func_mapping[agg_fct]
            query_format = [sql_func(table_obj.c[col]) for col in column_names]

        query = select(*query_format)

        if where_operator:
            query = self.query_with_where_clause(query, table_name, where_column_name, where_operator, where_value)

        result = self.engine.execute(query).fetchall() if execute_query else query

        return result

    def query_with_where_clause(
        self,
        sql_query: Union[Insert, Select, Delete],
        table_name: str,
        column_name: str,
        operator: str,
        value: Union[int, str, list],
    ) -> Union[Insert, Select, Delete]:
        """
        Add SQL 'where' clause to query

        :param query: (Union[Insert, Select, Delete]) SQLAlchemy basic query
        :param table_name: (str) The SQL table name with the column to extract data from.
        :param column_name: (str) SQL column name to be used for the 'where' operation.
        :param operator: (str) SQL operator (ex. >, <=, ==, in, between).
        :param value: (Union[int, str, list]) Value(s) to be used in the 'where' clause.

        :return: (Union[Insert, Select, Delete]) Formatted SQL Alchemy basic query with the 'where' clause added.
        """
        table_obj = self.get_table_object(table_name)
        if operator == "between":
            start, end = str(min(value)), str(max(value))
            where_clause = table_obj.columns[column_name].between(start, end)
        elif operator == "in":
            where_clause = table_obj.columns[column_name].in_(value)
        else:
            raise ValueError(f"Invalid operator '{operator}' value. Not implemented.")

        return sql_query.where(where_clause)

    def delete(
        self, table_name: str, column_name: str, where_value: Union[int, str, list], where_operator: str = "between"
    ) -> None:
        """
        Perform SQL delete statement.

        :param table_name: (str) Database table name.
        :param column_name: (str) Column from where to delete data.
        :param where_value: (Union[int, str, list]) value(s) to be used in the 'where' clause.
        :param where_operator: (str) Either or not to use an SQL operator (ex. >, <=, ==, in, between).
        By default, set to ``"between"``.
        """
        table_obj = self.get_table_object(table_name)
        query = delete(table_obj)
        query_where = self.query_with_where_clause(query, table_name, column_name, where_operator, where_value)

        self.engine.execute(query_where)
        self.engine.commit()

    def get_all_tables(self) -> List:
        """
        Get all table names of the schema.

        :return: List of all the tables name in the database.
        """
        return self.schema.get_table_names()

    def execute_query_with_string(self, query_str: str) -> CursorResult[Any]:
        """
        Perform SQL raw statement (usually more complex statement).

        :param query_str: (str) SQL raw query (ex. INSERT * INTO TABLE123).

        :return: Executed query - Note : use fetchall() on the return if select query.
        """
        query = text(query_str)
        return self.engine.execute(query)

    def get_table_object(self, table_name: str) -> Table:
        """
        Get SQLAlchemy table object.

        :param table_name: (str) Name of a table in the database.

        :return: A SQLAlchemy table object.
        """
        return Table(
            table_name,
            self.metadata,
        )

    @staticmethod
    def get_column_names(table_object: Table) -> List[str]:
        """
        Get column names from a table.

        :param table_object: (Table) SQLAlchemy table object

        :return: Columns names of the table.
        """
        return table_object.columns.keys()

    @staticmethod
    def _order_data(column_names: List[str], data: List[dict]) -> List[dict]:
        """
        Order data in a table.

        :param column_names: (List[str]) Columns pattern to order data.
        :param data: (List[dict]) List of data to be ordered in the columns.

        :return: List of ordered data respecting the pattern.
        """
        values = []
        for obs in data:
            obs_dict = {}
            for col_name in reversed(column_names):
                if col_name in obs:
                    obs_dict[col_name] = obs[col_name]

            values.append(obs_dict)
        return values
