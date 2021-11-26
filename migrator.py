import logging
from types import resolve_bases
import psycopg2
import os
from typing import List

READ_MODE = "r"
UP_MIGRATION = "up"
DOWN_MIGRATION = "down"

class Migrator:
    def __init__(self, db_connection, migrations_path: str) -> None:
        self.migrations_path = migrations_path
        self.db_connection = db_connection

    def migrate_with_clean_start(self) -> None:
        self.migrate_down()
        self.migrate_up()
    
    def migrate_up(self) -> None:
        migration_files = self._get_up_migration_files()
        sorted_migration_files = sorted(migration_files)

        self._do_migrate(sorted_migration_files)

    def migrate_down(self) -> None:
        migration_files = self._get_down_migration_files()
        sorted_migration_files = sorted(migration_files, reverse=True)

        self._do_migrate(sorted_migration_files)

    def _get_up_migration_files(self) -> List:
        return self._get_migration_files(UP_MIGRATION)

    def _get_down_migration_files(self) -> List:
        return self._get_migration_files(DOWN_MIGRATION)

    def _get_migration_files(self, expected_migration_type: str) -> List:
        migration_files = []

        if not os.path.isdir(self.migrations_path):
            msg = f"migrations path `{self.migrations_path}` is not a directory"
            raise NotADirectoryError(msg)

        migrations_dir_contents_list = os.listdir(self.migrations_path)
        for content in migrations_dir_contents_list:
            path = os.path.join(self.migrations_path, content)

            if not os.path.isfile(path):
                continue

            file_parts = path.split(".")
            if len(file_parts) < 3:
                continue

            file_extension = file_parts[-1]
            if file_extension != "sql":
                continue

            file_migration_type = file_parts[-2]
            if file_migration_type == expected_migration_type:
                migration_files.append(path)

        return migration_files

    def _do_migrate(self, sorted_migration_files: List) -> None:
        cursor = self.db_connection.cursor()

        try:
            for migration_file in sorted_migration_files:
                with open(migration_file, READ_MODE) as f:
                    query = f.read()
                    cursor.execute(query)

            self.db_connection.commit()

        except NotADirectoryError as error:
            logging.error(f"got not a directory error during migration: {error}")
            raise error

        except psycopg2.DatabaseError as error:
            logging.error(f"got db error during migration: {error}")
            self.db_connection.rollback()
            raise error

        finally:
            cursor.close()

if __name__ == "__main__":
    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5400/postgres")

    try:
        migrator = Migrator(conn, "./migrations")
        migrator.migrate_with_clean_start()

    except (psycopg2.DatabaseError, NotADirectoryError) as error:
        print(f"Got a nice error: {error}")
    
    print("well, here we are")

