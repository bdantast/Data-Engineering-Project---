import psycopg2
import psycopg2.extras
import pandas as pd
from contextlib import contextmanager
from config import DB_CONFIG


class Database:
    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self._conn = None

    def connect(self):
        try:
            self._conn = psycopg2.connect(**self.config)
            self._conn.autocommit = True
            return True
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Falha ao conectar no PostgreSQL: {e}")

    def disconnect(self):
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None

    @contextmanager
    def cursor(self, dict_cursor=True):
        if not self._conn or self._conn.closed:
            self.connect()
        cur_factory = psycopg2.extras.RealDictCursor if dict_cursor else None
        cur = self._conn.cursor(cursor_factory=cur_factory)
        try:
            yield cur
        finally:
            cur.close()

    def query(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                return [dict(row) for row in cur.fetchall()]
            return []

    def query_df(self, sql, params=None):
        with self.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return pd.DataFrame(rows, columns=columns)
            return pd.DataFrame()

    def test_connection(self):
        try:
            with self.cursor() as cur:
                cur.execute("SELECT version();")
                result = cur.fetchone()
                return True, result.get("version", "OK")
        except Exception as e:
            return False, str(e)

    @property
    def connected(self):
        return self._conn is not None and not self._conn.closed


db = Database()
