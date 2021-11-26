import pandas as pd
import logging
import psycopg2
import geopandas as gpd

MARKERS_GEOM_COL = "point"

class LoadMarkersCommand:
    def __init__(self, db_connection) -> None:
        self.db_connection = db_connection
    
    def run(self) -> None:
        cursor = self.db_connection.cursor()

        try:
            active_markers = self._get_active_markers()
            active_markers.apply(self._insert_marker, axis=1, args=(cursor,))

            deleted_markers = self._get_deleted_markers()
            deleted_markers.apply(self._delete_marker, axis=1, args=(cursor,))
            
            self.db_connection.commit()

        except psycopg2.DatabaseError as error:
            logging.error(f"got db error during loading of markers: {error}")
            self.db_connection.rollback()

        finally:
            cursor.close()

    def _get_active_markers(self):
        select_active_markers_query = """
            SELECT id, created_at, updated_at, point FROM public.markers
            WHERE 1=1
            AND deleted_at IS NULL
            """

        active_markers = gpd.GeoDataFrame.from_postgis(
            select_active_markers_query, self.db_connection, geom_col=MARKERS_GEOM_COL)

        return active_markers

    def _insert_marker(self, row, cursor):
        insert_statement_base = """
        WITH
        point as (
            SELECT ST_GeomFromText(%s, 4326) as geometry
        ),
        region AS (
            SELECT name FROM dwh.regions
            WHERE ST_Contains(location::geometry, (SELECT geometry FROM point))
        )
        INSERT INTO dwh.markers (id, created_at, updated_at, point, region)
            VALUES (%s, %s, %s, %s, (SELECT name FROM region))
        ON CONFLICT (id)
        DO UPDATE SET
            created_at = %s,
            updated_at = %s,
            point = %s,
            region = (SELECT name FROM region)
        """

        params = self._translate_row_to_insert_params(row)
        cursor.execute(insert_statement_base, params)

    def _translate_row_to_insert_params(self, row):
        params = (str(row["point"]), row["id"]) + (
            row["created_at"],
            row["updated_at"],
            str(row["point"])
        ) * 2
        
        return params

    def _get_deleted_markers(self):
        select_deleted_markers_query = """
            SELECT id FROM public.markers
            WHERE 1=1
            AND deleted_at IS NOT NULL
            """

        deleted_markers = pd.read_sql(select_deleted_markers_query, self.db_connection)
        return deleted_markers

    def _delete_marker(self, row, cursor):
        delete_marker_statement_base = """
        DELETE FROM dwh.markers
        WHERE id = %s
        """

        cursor.execute(delete_marker_statement_base, (row["id"],))

if __name__ == "__main__":
    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5400/postgres")

    load_markers_command = LoadMarkersCommand(conn)
    load_markers_command.run()
