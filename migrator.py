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
    
    def migrate(self) -> None:
        cursor = self.db_connection.cursor()

        try:
            migration_files = self._get_up_migration_files()
            sorted_migration_files = sorted(migration_files)

            for migration_file in sorted_migration_files:
                with open(migration_file, READ_MODE) as f:
                    query = f.read()
                    cursor.execute(query)
            
            self.db_connection.commit()

        except NotADirectoryError as error:
            # TODO: log error
            raise error
            
        except psycopg2.DatabaseError as error:
            # TODO: log error
            print(f"got db error: {error}")
            self.db_connection.rollback()

        finally:
            cursor.close()

    def down_migrate(self) -> None:
        cursor = self.db_connection.cursor()

        try:
            migration_files = self._get_down_migration_files()
            sorted_migration_files = sorted(migration_files, reverse=True)

            for migration_file in sorted_migration_files:
                with open(migration_file, READ_MODE) as f:
                    query = f.read()
                    cursor.execute(query)

            self.db_connection.commit()

        except NotADirectoryError as error:
            # TODO: log error
            raise error

        except psycopg2.DatabaseError as error:
            # TODO: log error
            print(f"got db error: {error}")
            self.db_connection.rollback()

        finally:
            cursor.close()

    def _get_up_migration_files(self) -> List:
        return self._get_migration_files(UP_MIGRATION)

    def _get_down_migration_files(self) -> List:
        return self._get_migration_files(DOWN_MIGRATION)
        
    def _get_migration_files(self, expected_migration_type: str) -> List:
        migration_files = []

        if not os.path.isdir(self.migrations_path):
            raise NotADirectoryError("Migrations path is not a directory")

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

if __name__ == "__main__":
    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5400/postgres")

    try:
        migrator = Migrator(conn, "./migrations")
        migrator.down_migrate()
        migrator.migrate()

    except (psycopg2.DatabaseError, NotADirectoryError) as error:
        print(f"Got a nice error: {error}")
    
    print("well, here we are")

