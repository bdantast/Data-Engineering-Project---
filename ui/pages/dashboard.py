import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
from ui.widgets.kpi_card import KPICard, MiniSparkline
from ui.widgets.chart_frame import ChartFrame
from ui.widgets.data_table import DataTable
from core.database import db
from core.schema_discover import schema_discover
from core.kpi_engine import kpi_engine
from core.charts import create_line_chart, create_bar_chart, create_pie_chart
from config import COLORS
import pandas as pd
import random


class DashboardPage(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style="TFrame")
        self.kpi_cards = {}
        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill=X, padx=20, pady=(15, 5))
        ttk.Label(
            header, text="Dashboard - Visao Geral",
            font=("Segoe UI", 16, "bold"),
            foreground=COLORS["text_primary"], background=COLORS["bg_dark"],
        ).pack(side=LEFT)
        ttk.Button(
            header, text="Atualizar", bootstyle="warning",
            command=self.load_data, width=12,
        ).pack(side=LEFT, padx=15)

        charts_row = ttk.Frame(self, style="TFrame")
        charts_row.pack(fill=X, padx=20, pady=5)
        self.chart1 = ChartFrame(charts_row, title="Tendencia")
        self.chart1.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        self.chart2 = ChartFrame(charts_row, title="Distribuicao")
        self.chart2.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))

        table_section = ttk.Frame(self, style="TFrame")
        table_section.pack(fill=BOTH, expand=True, padx=20, pady=5)
        ttk.Label(
            table_section, text="Dados Recentes",
            font=("Segoe UI", 11, "bold"),
            foreground=COLORS["neon_blue"], background=COLORS["bg_dark"],
        ).pack(anchor=W, pady=(0, 5))
        self.data_table = DataTable(table_section)
        self.data_table.pack(fill=BOTH, expand=True)

        kpi_row = ttk.Frame(self, style="Card.TFrame")
        kpi_row.pack(fill=X, padx=20, pady=(5, 15))

        self.kpi_container = ttk.Frame(kpi_row, style="Card.TFrame")
        self.kpi_container.pack(fill=X, padx=10, pady=10)

        self.status_var = ttk.StringVar(value="Pronto")
        ttk.Label(
            self, textvariable=self.status_var, font=("Segoe UI", 8),
            foreground=COLORS["text_muted"], background=COLORS["bg_dark"],
        ).pack(anchor=W, padx=20, pady=(0, 5))

    def load_data(self):
        self.status_var.set("Carregando dados...")
        threading.Thread(target=self._load_async, daemon=True).start()

    def _load_async(self):
        try:
            if not schema_discover.tables:
                schema_discover.discover()
            if not kpi_engine.kpis:
                kpi_engine.calculate_all()
            self.after(0, self._update_ui)
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Erro: {e}"))

    def _update_ui(self):
        try:
            self._update_kpi_cards()
            self._update_charts()
            self._update_table()
            self.status_var.set(
                f"Atualizado - {len(schema_discover.tables)} tabelas"
            )
        except Exception as e:
            self.status_var.set(f"Erro: {e}")

    def _update_kpi_cards(self):
        for widget in self.kpi_container.winfo_children():
            widget.destroy()

        total_receita = 0
        total_registros = 0
        margem = 0
        total_lucro = 0

        for table, kpis in kpi_engine.kpis.items():
            vendas = kpis.get("vendas", {})
            fin = kpis.get("financeiro", {})
            resumo = kpis.get("resumo", {})
            total_registros += resumo.get("total_registros", 0)
            margem = fin.get("margem_percentual", margem)
            total_lucro = fin.get("lucro", total_lucro)
            for key, val in vendas.items():
                if key.endswith("_total") and isinstance(val, (int, float)):
                    total_receita += val

        spark_data_1 = [random.randint(80, 150) for _ in range(10)]
        spark_data_2 = [random.randint(50, 120) for _ in range(10)]
        spark_data_3 = [random.randint(30, 90) for _ in range(10)]
        spark_data_4 = [random.randint(60, 100) for _ in range(10)]

        cards = [
            ("Total Revenue", f"${total_receita:,.2f}", spark_data_1, COLORS["neon_blue"]),
            ("Active Projects", f"{total_registros}", spark_data_2, COLORS["neon_green"]),
            ("Profit Margin", f"{margem:.1f}%", spark_data_3, COLORS["neon_purple"]),
            ("Net Profit", f"${total_lucro:,.2f}", spark_data_4, COLORS["neon_orange"]),
        ]

        for i, (label, value, spark, color) in enumerate(cards):
            card_frame = ttk.Frame(self.kpi_container, style="Card.TFrame")
            card_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

            inner = ttk.Frame(card_frame, style="Card.TFrame")
            inner.pack(fill=BOTH, expand=True, padx=10, pady=8)

            ttk.Label(
                inner, text=label, font=("Segoe UI", 9),
                foreground=COLORS["text_muted"], background=COLORS["bg_card"],
            ).pack(anchor=W)
            ttk.Label(
                inner, text=value, font=("Segoe UI", 20, "bold"),
                foreground=color, background=COLORS["bg_card"],
            ).pack(anchor=W, pady=(2, 0))

            spark_frame = MiniSparkline(inner, data=spark, color=color)
            spark_frame.pack(fill=X, pady=(5, 0))

    def _update_charts(self):
        for table, kpis in kpi_engine.kpis.items():
            vendas = kpis.get("vendas", {})
            top_cats = vendas.get("top_categorias", [])
            amount_cols = vendas.get("colunas_valor", [])
            date_col = vendas.get("coluna_data")

            if top_cats and len(top_cats) > 1:
                df_cats = pd.DataFrame(top_cats)
                if "categoria" in df_cats.columns and "total" in df_cats.columns:
                    fig = create_pie_chart(
                        df_cats.head(6), "categoria", "total",
                        title=f"Distribuicao - {table}",
                    )
                    self.chart2.set_figure(fig)

            if amount_cols and date_col:
                try:
                    df_ts = kpi_engine.get_time_series(table, amount_cols[0], date_col)
                    if not df_ts.empty and "periodo" in df_ts.columns and "total" in df_ts.columns:
                        fig = create_line_chart(
                            df_ts, "periodo", "total",
                            title=f"Tendencia - {table}",
                        )
                        self.chart1.set_figure(fig)
                except Exception:
                    pass

    def _update_table(self):
        if schema_discover.tables:
            first_table = schema_discover.tables[0]
            try:
                df = schema_discover.get_table_preview(first_table, limit=50)
                self.data_table.set_data(df)
            except Exception:
                pass
