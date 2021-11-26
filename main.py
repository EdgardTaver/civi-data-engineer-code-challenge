import os
import logging

import psycopg2
from dotenv import find_dotenv, load_dotenv

from migrator import Migrator
from users_loader import UsersLoader
from load_regions_command import LoadRegionsCommand
from load_markers_command import LoadMarkersCommand
from connection import MainConnection, RawDataConnection, DWHConnection

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    conn_string = os.getenv("DB_CONN_STRING")
    migrations_path = os.getenv("MIGRATIONS_PATH")
    log_level_from_env = os.getenv("LOG_LEVEL")
    users_data_path = os.getenv("USERS_DATA_PATH")
    log_format = os.getenv("LOG_FORMAT")
    raw_data_dbname = os.getenv("RAW_DATA_DBNAME")
    dwh_dbname = os.getenv("DWH_DBNAME")
    
    log_level = logging.DEBUG if log_level_from_env == "debug" else logging.INFO
    logging.basicConfig(level=log_level, format=log_format)

    main_connection = MainConnection(conn_string)
    dwh_connection = DWHConnection(main_connection, dwh_dbname)
    raw_data_connection = RawDataConnection(main_connection, raw_data_dbname)

    try:
        migrator = Migrator(dwh_connection, migrations_path)
        migrator.migrate_with_clean_start()

        load_regions_command = LoadRegionsCommand(dwh_connection, raw_data_connection)
        load_regions_command.run()

        load_markers_command = LoadMarkersCommand(dwh_connection, raw_data_connection)
        load_markers_command.run()

        users_loader = UsersLoader(dwh_connection, users_data_path)
        users_loader.load()

        main_connection.close()
        dwh_connection.close()
        raw_data_connection.close()

    except Exception as error:
        logging.error(f"got error during full DWH process: {error}")
    
    logging.info("everything fine")
