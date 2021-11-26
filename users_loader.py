import os
import json
import pandas as pd
import psycopg2
from typing import List, Dict, Tuple
import logging
from connection import DWHConnection

READ_MODE = "r"

class UsersLoader:
    def __init__(self, dwh_connection: DWHConnection, file_path: str) -> None:
        self.dwh_connection = dwh_connection
        self.file_path = file_path

    def load(self) -> None:
        json_data = self._load_json_data()
        users = self._build_dataset(json_data)

        cursor = self.dwh_connection.cursor()

        try:
            users.apply(self._insert_user, axis=1, args=(cursor,))            
            self.dwh_connection.commit()

        except psycopg2.DatabaseError as error:
            logging.error(f"got db error: {error}")
            self.dwh_connection.rollback()

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
        
    def _insert_user(self, row: List, cursor: psycopg2.extensions.cursor) -> None:
        insert_statement_base = """
        WITH
        point as (
            SELECT ST_GeomFromText('POINT(%s %s)', 4326) as geometry
        ),
        region AS (
            SELECT name FROM dwh.regions
            WHERE ST_Contains(location::geometry, (SELECT geometry FROM point))
        )
        INSERT INTO dwh.users (username, phone, point, region) 
            VALUES(%s, %s, (SELECT geometry FROM point), (SELECT name FROM region))
        ON CONFLICT (username) 
        DO UPDATE SET
            point = (SELECT geometry FROM point),
            region = (SELECT name FROM region),
            updated_at = NOW()
        """

        params = self._translate_row_to_insert_params(row)
        cursor.execute(insert_statement_base, params)

    def _translate_row_to_insert_params(self, row: List) -> Tuple:
        params = (
            row["longitude"],
            row["latitude"],
            row["username"],
            row["phone"],
        )
        
        return params


if __name__ == "__main__":
    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5400/postgres")

    path = os.path.join(os.path.dirname(__file__), "data", "users.json")
    loader = UsersLoader(conn, path)
    loader.load()
