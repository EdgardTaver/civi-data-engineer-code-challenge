import os
import logging

import psycopg2
from dotenv import find_dotenv, load_dotenv

from migrator import Migrator
from users_loader import UsersLoader

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    conn_string = os.getenv("DB_CONN_STRING")
    migrations_path = os.getenv("MIGRATIONS_PATH")
    log_level_from_env = os.getenv("LOG_LEVEL")
    users_data_path = os.getenv("USERS_DATA_PATH")
    
    log_level = logging.DEBUG if log_level_from_env == "debug" else logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    db_connection = psycopg2.connect(conn_string)

    try:
        migrator = Migrator(db_connection, migrations_path)
        migrator.migrate_with_clean_start()

        users_loader = UsersLoader(db_connection, users_data_path)
        users_loader.load()

    except (psycopg2.DatabaseError, NotADirectoryError) as error:
        print(f"Got a nice error: {error}")
    
    logging.info("everything fine")
