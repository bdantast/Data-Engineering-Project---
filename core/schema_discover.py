from psycopg2 import sql
from core.database import db
from core.security import validate_identifier


class SchemaDiscover:
    def __init__(self):
        self.tables = []
        self.schema_info = {}

    def discover(self):
        self.tables = self._get_tables()
        self.schema_info = {}
        for table in self.tables:
            self.schema_info[table] = self._get_columns(table)
        return self.schema_info

    def _get_tables(self):
        sql_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        rows = db.query(sql_query)
        return [r["table_name"] for r in rows]

    def _get_columns(self, table):
        validate_identifier(table, "table name")
        sql_query = sql.SQL("""
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                COALESCE(
                    (SELECT pg_catalog.col_description(
                        (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass,
                        c.ordinal_position
                    )),
                    ''
                ) as column_comment
            FROM information_schema.columns c
            WHERE c.table_schema = 'public'
              AND c.table_name = %s
            ORDER BY c.ordinal_position;
        """)
        return db.query(sql_query, (table,))

    def get_table_preview(self, table, limit=50):
        validate_identifier(table, "table name")
        sql_query = sql.SQL("SELECT * FROM {} LIMIT %s").format(
            sql.Identifier(table)
        )
        return db.query_df(sql_query, (limit,))

    def get_row_count(self, table):
        validate_identifier(table, "table name")
        sql_query = sql.SQL("SELECT COUNT(*) as total FROM {}").format(
            sql.Identifier(table)
        )
        result = db.query(sql_query)
        return result[0]["total"] if result else 0

    def get_numeric_columns(self, table):
        numeric_types = [
            "integer", "bigint", "smallint",
            "numeric", "decimal", "real", "double precision",
            "money",
        ]
        cols = self.schema_info.get(table, [])
        return [c["column_name"] for c in cols if c["data_type"] in numeric_types]

    def get_date_columns(self, table):
        date_types = ["date", "timestamp without time zone", "timestamp with time zone"]
        cols = self.schema_info.get(table, [])
        return [c["column_name"] for c in cols if c["data_type"] in date_types]

    def get_text_columns(self, table):
        text_types = ["character varying", "text", "character"]
        cols = self.schema_info.get(table, [])
        return [c["column_name"] for c in cols if c["data_type"] in text_types]

    def detect_amount_columns(self, table):
        amount_keywords = [
            "price", "preco", "valor", "amount", "total", "revenue",
            "receita", "lucro", "profit", "cost", "custo", "desconto",
            "discount", "frete", "shipping", "tax", "imposto", "fee",
        ]
        num_cols = self.get_numeric_columns(table)
        return [c for c in num_cols if any(kw in c.lower() for kw in amount_keywords)]

    def detect_date_column(self, table):
        date_keywords = [
            "date", "data", "created", "criado", "order", "pedido",
            "sale", "venda", "time", "hora", "timestamp",
        ]
        date_cols = self.get_date_columns(table)
        for col in date_cols:
            if any(kw in col.lower() for kw in date_keywords):
                return col
        return date_cols[0] if date_cols else None

    def detect_category_column(self, table):
        cat_keywords = [
            "category", "categoria", "type", "tipo", "status",
            "region", "regiao", "cidade", "city", "state", "estado",
            "product", "produto", "vendedor", "seller", "customer",
            "cliente", "forma", "payment", "pagamento",
        ]
        text_cols = self.get_text_columns(table)
        for col in text_cols:
            if any(kw in col.lower() for kw in cat_keywords):
                return col
        return text_cols[0] if text_cols else None


schema_discover = SchemaDiscover()
