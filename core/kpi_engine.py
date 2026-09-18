import pandas as pd
from core.database import db
from core.schema_discover import schema_discover


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
                sql = f"""
                    SELECT
                        SUM({col}) as total,
                        AVG({col}) as media,
                        MIN({col}) as minimo,
                        MAX({col}) as maximo
                    FROM {table};
                """
                result = db.query(sql)
                if result:
                    kpis[f"{col}_total"] = float(result[0]["total"] or 0)
                    kpis[f"{col}_media"] = float(result[0]["media"] or 0)
                    kpis[f"{col}_minimo"] = float(result[0]["minimo"] or 0)
                    kpis[f"{col}_maximo"] = float(result[0]["maximo"] or 0)
        if date_col:
            sql = f"""
                SELECT
                    MIN({date_col}) as primeira_data,
                    MAX({date_col}) as ultima_data
                FROM {table};
            """
            result = db.query(sql)
            if result:
                kpis["primeira_data"] = str(result[0]["primeira_data"] or "")
                kpis["ultima_data"] = str(result[0]["ultima_data"] or "")
        if cat_col and amount_cols:
            main_amount = amount_cols[0]
            sql = f"""
                SELECT {cat_col} as categoria,
                       SUM({main_amount}) as total
                FROM {table}
                GROUP BY {cat_col}
                ORDER BY total DESC
                LIMIT 10;
            """
            kpis["top_categorias"] = db.query(sql)
        return kpis

    def _financeiro_kpis(self, table):
        amount_cols = schema_discover.detect_amount_columns(table)
        kpis = {"colunas_valor": amount_cols}
        if len(amount_cols) >= 2:
            receita_col = amount_cols[0]
            custo_col = amount_cols[1]
            sql = f"""
                SELECT
                    SUM({receita_col}) as receita_total,
                    SUM({custo_col}) as custo_total,
                    SUM({receita_col}) - SUM({custo_col}) as lucro,
                    CASE
                        WHEN SUM({receita_col}) > 0
                        THEN ROUND(((SUM({receita_col}) - SUM({custo_col})) / SUM({receita_col}) * 100)::numeric, 2)
                        ELSE 0
                    END as margem_percentual
                FROM {table};
            """
            result = db.query(sql)
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
        if period == "month":
            trunc = "month"
        elif period == "week":
            trunc = "week"
        else:
            trunc = "day"
        sql = f"""
            SELECT
                DATE_TRUNC('{trunc}', {date_col}) as periodo,
                SUM({amount_col}) as total,
                COUNT(*) as quantidade
            FROM {table}
            WHERE {date_col} IS NOT NULL
            GROUP BY periodo
            ORDER BY periodo;
        """
        return db.query_df(sql)

    def get_category_breakdown(self, table, amount_col, cat_col):
        sql = f"""
            SELECT
                {cat_col} as categoria,
                SUM({amount_col}) as total,
                COUNT(*) as quantidade,
                ROUND(AVG({amount_col})::numeric, 2) as media
            FROM {table}
            WHERE {cat_col} IS NOT NULL
            GROUP BY {cat_col}
            ORDER BY total DESC;
        """
        return db.query_df(sql)


kpi_engine = KPIEngine()
