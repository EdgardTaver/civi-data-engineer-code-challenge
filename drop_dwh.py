import os
import logging
from connection import MainConnection, DWHConnection
from dotenv import find_dotenv, load_dotenv

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    conn_string = os.getenv("DB_CONN_STRING")
    dwh_dbname = os.getenv("DWH_DBNAME")
    log_level_from_env = os.getenv("LOG_LEVEL")
    log_format = os.getenv("LOG_FORMAT")

    log_level = logging.DEBUG if log_level_from_env == "debug" else logging.INFO
    logging.basicConfig(level=log_level, format=log_format)

    try:
        main_connection = MainConnection(conn_string)
        dwh_connection = DWHConnection(main_connection, dwh_dbname)

        dwh_connection.close()
        dwh_connection.drop_db()

        main_connection.close()

    except Exception as error:
        logging.error(f"got error during full DWH process: {error}")

    logging.info("DWH ropped")
