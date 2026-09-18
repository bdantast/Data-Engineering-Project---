import pandas as pd
from psycopg2 import sql
from core.database import db
from core.schema_discover import schema_discover
from core.security import validate_identifier


class KPIEngine:
    def __init__(self):
        self.kpis = {}

    def calculate_all(self, table=None):
        if table:
            tables = [table]
        else:
            tables = schema_discover.tables

        all_kpis = {}
        for t in tables:
            all_kpis[t] = {
                "vendas": self._vendas_kpis(t),
                "financeiro": self._financeiro_kpis(t),
                "resumo": self._resumo_kpis(t),
            }
        self.kpis = all_kpis
        return all_kpis

    def _vendas_kpis(self, table):
        validate_identifier(table, "table name")
        amount_cols = schema_discover.detect_amount_columns(table)
        date_col = schema_discover.detect_date_column(table)
        cat_col = schema_discover.detect_category_column(table)
        kpis = {
            "total_registros": schema_discover.get_row_count(table),
            "colunas_valor": amount_cols,
            "coluna_data": date_col,
            "coluna_categoria": cat_col,
        }
        if amount_cols:
            for col in amount_cols:
                validate_identifier(col, "column name")
                sql_query = sql.SQL("""
                    SELECT
                        SUM({col}) as total,
                        AVG({col}) as media,
                        MIN({col}) as minimo,
                        MAX({col}) as maximo
                    FROM {tbl};
                """).format(col=sql.Identifier(col), tbl=sql.Identifier(table))
                result = db.query(sql_query)
                if result:
                    kpis[f"{col}_total"] = float(result[0]["total"] or 0)
                    kpis[f"{col}_media"] = float(result[0]["media"] or 0)
                    kpis[f"{col}_minimo"] = float(result[0]["minimo"] or 0)
                    kpis[f"{col}_maximo"] = float(result[0]["maximo"] or 0)
        if date_col:
            validate_identifier(date_col, "column name")
            sql_query = sql.SQL("""
                SELECT
                    MIN({date_col}) as primeira_data,
                    MAX({date_col}) as ultima_data
                FROM {tbl};
            """).format(date_col=sql.Identifier(date_col), tbl=sql.Identifier(table))
            result = db.query(sql_query)
            if result:
                kpis["primeira_data"] = str(result[0]["primeira_data"] or "")
                kpis["ultima_data"] = str(result[0]["ultima_data"] or "")
        if cat_col and amount_cols:
            main_amount = amount_cols[0]
            validate_identifier(cat_col, "column name")
            validate_identifier(main_amount, "column name")
            sql_query = sql.SQL("""
                SELECT {cat_col} as categoria,
                       SUM({main_amount}) as total
                FROM {tbl}
                GROUP BY {cat_col}
                ORDER BY total DESC
                LIMIT 10;
            """).format(
                cat_col=sql.Identifier(cat_col),
                main_amount=sql.Identifier(main_amount),
                tbl=sql.Identifier(table),
            )
            kpis["top_categorias"] = db.query(sql_query)
        return kpis

    def _financeiro_kpis(self, table):
        validate_identifier(table, "table name")
        amount_cols = schema_discover.detect_amount_columns(table)
        kpis = {"colunas_valor": amount_cols}
        if len(amount_cols) >= 2:
            receita_col = amount_cols[0]
            custo_col = amount_cols[1]
            validate_identifier(receita_col, "column name")
            validate_identifier(custo_col, "column name")
            sql_query = sql.SQL("""
                SELECT
                    SUM({receita}) as receita_total,
                    SUM({custo}) as custo_total,
                    SUM({receita}) - SUM({custo}) as lucro,
                    CASE
                        WHEN SUM({receita}) > 0
                        THEN ROUND(((SUM({receita}) - SUM({custo})) / SUM({receita}) * 100)::numeric, 2)
                        ELSE 0
                    END as margem_percentual
                FROM {tbl};
            """).format(
                receita=sql.Identifier(receita_col),
                custo=sql.Identifier(custo_col),
                tbl=sql.Identifier(table),
            )
            result = db.query(sql_query)
            if result:
                kpis["receita_total"] = float(result[0]["receita_total"] or 0)
                kpis["custo_total"] = float(result[0]["custo_total"] or 0)
                kpis["lucro"] = float(result[0]["lucro"] or 0)
                kpis["margem_percentual"] = float(result[0]["margem_percentual"] or 0)
        return kpis

    def _resumo_kpis(self, table):
        total = schema_discover.get_row_count(table)
        num_cols = schema_discover.get_numeric_columns(table)
        date_col = schema_discover.detect_date_column(table)
        cat_col = schema_discover.detect_category_column(table)
        return {
            "total_registros": total,
            "colunas_numericas": len(num_cols),
            "colunas_texto": len(schema_discover.get_text_columns(table)),
            "colunas_data": len(schema_discover.get_date_columns(table)),
            "coluna_data_detectada": date_col,
            "coluna_categoria_detectada": cat_col,
        }

    def get_time_series(self, table, amount_col, date_col, period="month"):
        validate_identifier(table, "table name")
        validate_identifier(amount_col, "column name")
        validate_identifier(date_col, "column name")
        if period == "month":
            trunc = "month"
        elif period == "week":
            trunc = "week"
        else:
            trunc = "day"
        sql_query = sql.SQL("""
            SELECT
                DATE_TRUNC({trunc}, {date_col}) as periodo,
                SUM({amount_col}) as total,
                COUNT(*) as quantidade
            FROM {tbl}
            WHERE {date_col} IS NOT NULL
            GROUP BY periodo
            ORDER BY periodo;
        """).format(
            trunc=sql.Literal(trunc),
            date_col=sql.Identifier(date_col),
            amount_col=sql.Identifier(amount_col),
            tbl=sql.Identifier(table),
        )
        return db.query_df(sql_query)

    def get_category_breakdown(self, table, amount_col, cat_col):
        validate_identifier(table, "table name")
        validate_identifier(amount_col, "column name")
        validate_identifier(cat_col, "column name")
        sql_query = sql.SQL("""
            SELECT
                {cat_col} as categoria,
                SUM({amount_col}) as total,
                COUNT(*) as quantidade,
                ROUND(AVG({amount_col})::numeric, 2) as media
            FROM {tbl}
            WHERE {cat_col} IS NOT NULL
            GROUP BY {cat_col}
            ORDER BY total DESC;
        """).format(
            cat_col=sql.Identifier(cat_col),
            amount_col=sql.Identifier(amount_col),
            tbl=sql.Identifier(table),
        )
        return db.query_df(sql_query)


kpi_engine = KPIEngine()
