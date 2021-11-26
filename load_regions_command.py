import pandas as pd
import logging
import psycopg2
import geopandas as gpd

REGIONS_GEOM_COL = "location"

class LoadRegionsCommand:
    def __init__(self, db_connection) -> None:
        self.db_connection = db_connection
    
    def run(self) -> None:
        cursor = self.db_connection.cursor()

        try:
            active_regions = self._get_active_regions()
            active_regions.apply(self._insert_region, axis=1, args=(cursor,))

            deleted_regions = self._get_deleted_regions()
            deleted_regions.apply(self._delete_region, axis=1, args=(cursor,))
            
            self.db_connection.commit()

        except psycopg2.DatabaseError as error:
            logging.error(f"got db error during loading of regions: {error}")
            self.db_connection.rollback()

        finally:
            cursor.close()

    def _get_active_regions(self):
        select_active_regions_query = """
            SELECT id, created_at, updated_at, name, location FROM public.regions
            WHERE 1=1
            AND deleted_at IS NULL
            """

        active_regions = gpd.GeoDataFrame.from_postgis(
            select_active_regions_query, self.db_connection, geom_col=REGIONS_GEOM_COL)

        return active_regions

    def _insert_region(self, row, cursor):
        insert_statement_base = """
        INSERT INTO dwh.regions (id, created_at, updated_at, name, location)
            VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            created_at = %s,
            updated_at = %s,
            name = %s,
            location = %s
        """

        params = self._translate_row_to_insert_params(row)
        cursor.execute(insert_statement_base, params)

    def _translate_row_to_insert_params(self, row):
        params = (row["id"],) + (
            row["created_at"],
            row["updated_at"],
            row["name"],
            str(row["location"])
        ) * 2
        
        return params

    def _get_deleted_regions(self):
        select_deleted_regions_query = """
            SELECT id FROM public.regions
            WHERE 1=1
            AND deleted_at IS NOT NULL
            """

        deleted_regions = pd.read_sql(select_deleted_regions_query, self.db_connection)
        return deleted_regions

    def _delete_region(self, row, cursor):
        delete_region_statement_base = """
        DELETE FROM dwh.regions
        WHERE id = %s
        """

        cursor.execute(delete_region_statement_base, (row["id"],))

if __name__ == "__main__":
    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5400/postgres")

    load_regions_command = LoadRegionsCommand(conn)
    load_regions_command.run()
