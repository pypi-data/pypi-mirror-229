from mysql import connector
from typing import Callable

class DB():
    def __init__(
            self,
            host: str,
            user: str,
            password: str,
            database: str,
            port: int = 3306
        ) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.__get_connection__ = lambda: connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )
        pass

    def fetch_all(self, sql: str, params: tuple | None = None) -> list:
        conn = self.__get_connection__()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(sql, params)

            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def fetch_all_2(
        self,
        table: str,
        columns: list[str],
        where: dict
    ):
        keys = ", ".join(columns)
        where_keys = " AND ".join([f"{k} = %s" for k in where.keys()])
        sql = f"SELECT {keys} FROM {table} WHERE {where_keys}"

        return self.fetch_all(sql, tuple(where.values()))

    def fetch_one_v2(
        self,
        table: str,
        columns: list[str],
        where: dict
    ) -> dict:
        keys = ", ".join(columns)
        where_keys = " AND ".join([f"{k} = %s" for k in where.keys()])
        sql = f"SELECT {keys} FROM {table} WHERE {where_keys}"

        return self.fetch_one(sql, tuple(where.values()))

    def fetch_one(self, sql: str, params: tuple | None = None) -> dict:
        conn = self.__get_connection__()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(sql, params)

            return cursor.fetchone() # type: ignore
        finally:
            cursor.close()
            conn.close()

    def execute(self, sql: str, params: tuple | None = None) -> int:
        conn = self.__get_connection__()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(sql, params)

            conn.commit()
            return cursor.lastrowid # type: ignore
        finally:
            cursor.close()
            conn.close()

    def execute_many(self, sql: str, params: list[tuple]) -> int:
        conn = self.__get_connection__()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.executemany(sql, params)

            conn.commit()
            return cursor.lastrowid # type: ignore
        finally:
            cursor.close()
            conn.close()

    def execute_many_with_progress(
            self,
            sql: str,
            params: list[tuple],
            progress: Callable | None = None
        ) -> int:
        conn = self.__get_connection__()
        cursor = conn.cursor(dictionary=True)

        try:
            for i, param in enumerate(params):
                cursor.execute(sql, param)

                if progress is not None:
                    progress(i, len(params))

            conn.commit()
            return cursor.lastrowid # type: ignore
        finally:
            cursor.close()
            conn.close()

    def insert(self, table: str, data: dict) -> int:
        keys = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"

        return self.execute(sql, tuple(data.values()))
    
    def insert_many(self, table: str, data: list[dict]) -> int:
        keys = ", ".join(data[0].keys())
        values = ", ".join(["%s"] * len(data[0]))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"

        return self.execute_many(sql, [tuple(d.values()) for d in data])
    
    def insert_many_with_progress(
            self,
            table: str,
            data: list[dict],
            progress: Callable | None = None
        ) -> int:
        keys = ", ".join(data[0].keys())
        values = ", ".join(["%s"] * len(data[0]))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"

        return self.execute_many_with_progress(
            sql,
            [tuple(d.values()) for d in data],
            progress
        )
    
    def update(self, table: str, data: dict, where: str) -> int:
        keys = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {keys} WHERE {where}"

        return self.execute(sql, tuple(data.values()))
    
    def update_many(self, table: str, data: list[dict], where: str) -> int:
        keys = ", ".join([f"{k} = %s" for k in data[0].keys()])
        sql = f"UPDATE {table} SET {keys} WHERE {where}"

        return self.execute_many(sql, [tuple(d.values()) for d in data])
    