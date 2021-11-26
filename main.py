import os
import logging

import psycopg2
from dotenv import find_dotenv, load_dotenv

from migrator import Migrator
from users_loader import UsersLoader
from load_regions_command import LoadRegionsCommand

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    conn_string = os.getenv("DB_CONN_STRING")
    migrations_path = os.getenv("MIGRATIONS_PATH")
    log_level_from_env = os.getenv("LOG_LEVEL")
    users_data_path = os.getenv("USERS_DATA_PATH")
    log_format = os.getenv("LOG_FORMAT")
    
    log_level = logging.DEBUG if log_level_from_env == "debug" else logging.INFO
    logging.basicConfig(level=log_level, format=log_format)

    db_connection = psycopg2.connect(conn_string)

    try:
        migrator = Migrator(db_connection, migrations_path)
        migrator.migrate_with_clean_start()

        load_regions_command = LoadRegionsCommand(db_connection)
        load_regions_command.run()

        users_loader = UsersLoader(db_connection, users_data_path)
        users_loader.load()

    except Exception as error:
        logging.error(f"got error during full DWH process: {error}")
    
    logging.info("everything fine")
