import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Connection:
    def get_connection(self) -> psycopg2.extensions.connection:
        raise NotImplementedError()

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None

    def cursor(self) -> psycopg2.extensions.cursor:
        return self.get_connection().cursor()

    def commit(self) -> None:
        self.get_connection().commit()

    def rollback(self) -> None:
        self.get_connection().rollback()

class MainConnection(Connection):
    def __init__(self, conn_string: str) -> None:
        self.conn_string = conn_string
        self.connection = None
    
    def get_connection(self) -> psycopg2.extensions.connection:
        if not self.connection:
            self._request_new_connection()

        return self.connection
    
    def _request_new_connection(self) -> None:
        conn = psycopg2.connect(self.conn_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        self.connection = conn

class RawDataConnection(Connection):
    def __init__(self, main_connection: MainConnection, source_data_dbname: str) -> None:
        self.main_connection = main_connection
        self.source_data_dbname = source_data_dbname
        self.connection = None

    def get_connection(self) -> psycopg2.extensions.connection:
        if not self.connection:
            self._request_new_connection()

        return self.connection

    def _request_new_connection(self) -> None:
        conn_string = self.main_connection.conn_string
        conn = psycopg2.connect(conn_string, dbname=self.source_data_dbname)

        self.connection = conn


class DWHConnection(Connection):
    def __init__(self, main_connection: MainConnection, dwh_dbname: str) -> None:
        self.main_connection = main_connection
        self.dwn_dbname = dwh_dbname
        self.connection = None

    def get_connection(self) -> psycopg2.extensions.connection:
        if not self.connection:
            self._request_new_connection()

        return self.connection

    def _request_new_connection(self) -> None:
        self._ensure_db_exists()

        conn_string = self.main_connection.conn_string
        conn = psycopg2.connect(conn_string, dbname=self.dwn_dbname)

        self.connection = conn

    def _ensure_db_exists(self) -> None:
        cursor = self.main_connection.cursor()

        if self._db_exits(cursor):
            return

        self._create_db(cursor)

        cursor.close()

    def _db_exits(self, cursor: psycopg2.extensions.cursor) -> bool:
        select = """
        SELECT 1 AS result FROM pg_database
        WHERE datname='dwh'
        """

        cursor.execute(select)
        result = cursor.fetchone()

        db_exits = result != None
        return db_exits

    def _create_db(self, cursor: psycopg2.extensions.cursor):
        cursor.execute(f"CREATE DATABASE {self.dwn_dbname}")
    
    def drop_db(self) -> None:
        cursor = self.main_connection.cursor()

        if not self._db_exits(cursor):
            return

        cursor.execute(f"DROP DATABASE {self.dwn_dbname}")
        cursor.close()

