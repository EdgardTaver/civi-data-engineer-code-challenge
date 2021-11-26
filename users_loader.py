import os
import json
import pandas as pd
import psycopg2
from typing import List, Dict

READ_MODE = "r"

class UsersLoader:
    def __init__(self, db_connection, file_path:str) -> None:
        self.db_connection = db_connection
        self.file_path = file_path

    def load(self) -> None:
        json_data = self._load_json_data()
        users = self._build_dataset(json_data)

        cursor = self.db_connection.cursor()

        try:
            users.apply(self._insert_user, axis=1, args=(cursor,))            
            self.db_connection.commit()

        except psycopg2.DatabaseError as error:
            # TODO: log error
            print(f"got db during insertion error: {error}")
            self.db_connection.rollback()

        finally:
            cursor.close()

    def _load_json_data(self):
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"`{self.file_path}` not found")

        with open(self.file_path, READ_MODE) as f:
            data = json.load(f)
        
        if "users" not in data.keys():
            raise KeyError("'users' key not found in the users data JSON")

        return data

    def _build_dataset(self, data: Dict) -> pd.DataFrame:
        users = pd.DataFrame(data["users"])

        position_not_null_mask = users["latitude"].isna() == False
        position_not_null_mask &= users["longitude"].isna() == False

        valid_users = users[position_not_null_mask].copy()
        return valid_users
        
    def _insert_user(self, row: List, cursor) -> None:
        insert_statement_base = """
        INSERT INTO dwh.users(username, phone, point) 
                VALUES(%s, %s, ST_GeomFromText('POINT(%s %s)', 4326))
        ON CONFLICT (username) 
        DO
            UPDATE SET point = ST_GeomFromText('POINT(%s %s)', 4326)
        """

        params = (
            row["username"],
            row["phone"],
            row["longitude"],
            row["latitude"],
            row["longitude"],
            row["latitude"]
        )

        cursor.execute(insert_statement_base, params)


if __name__ == "__main__":
    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5400/postgres")

    path = os.path.join(os.path.dirname(__file__), "data", "users.json")
    loader = UsersLoader(conn, path)
    loader.load()
        
