import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import pandas as pd
from ui.widgets.kpi_card import KPICard
from ui.widgets.chart_frame import ChartFrame, InteractiveChartFrame
from ui.widgets.data_table import DataTable
from core.database import db
from core.schema_discover import schema_discover
from core.kpi_engine import kpi_engine
from core.charts import (
    create_line_chart, create_bar_chart, create_pie_chart,
    create_multi_bar_chart,
)


class VendasPage(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.charts_export = []
        self._build_ui()

    def _build_ui(self):
        canvas = ttk.Canvas(self, highlightthickness=False)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        self.scrollable = ttk.Frame(canvas)
        self.scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        header = ttk.Frame(self.scrollable)
        header.pack(fill=X, padx=15, pady=(15, 5))
        ttk.Label(header, text="Analise de Vendas", font=("Segoe UI", 16, "bold")).pack(side=LEFT)
        ttk.Button(header, text="Atualizar", bootstyle="info-outline",
                   command=self.load_data, width=12).pack(side=RIGHT)

        self.kpi_frame = ttk.Frame(self.scrollable)
        self.kpi_frame.pack(fill=X, padx=15, pady=5)

        charts_row = ttk.Frame(self.scrollable)
        charts_row.pack(fill=X, padx=15, pady=5)
        self.chart_trend = InteractiveChartFrame(charts_row, title="Tendencia de Vendas")
        self.chart_trend.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        self.chart_category = InteractiveChartFrame(charts_row, title="Vendas por Categoria")
        self.chart_category.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))

        self.table_frame = ttk.Frame(self.scrollable)
        self.table_frame.pack(fill=BOTH, expand=True, padx=15, pady=5)
        ttk.Label(self.table_frame, text="Detalhamento", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(0, 5))
        self.data_table = DataTable(self.table_frame)
        self.data_table.pack(fill=BOTH, expand=True)

        self.status_var = ttk.StringVar(value="Pronto")

    def load_data(self):
        self.status_var.set("Carregando...")
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
        self.charts_export = []
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        col = 0
        for table, kpis in kpi_engine.kpis.items():
            vendas = kpis.get("vendas", {})
            amount_cols = vendas.get("colunas_valor", [])
            date_col = vendas.get("coluna_data")
            cat_col = vendas.get("coluna_categoria")

            for acol in amount_cols:
                total = vendas.get(f"{acol}_total", 0)
                media = vendas.get(f"{acol}_media", 0)
                card = KPICard(self.kpi_frame, label=f"{acol.title()} Total", value=f"R$ {total:,.2f}", bootstyle="primary")
                card.grid(row=0, column=col, padx=5, pady=5, sticky=NSEW)
                self.kpi_frame.columnconfigure(col, weight=1)
                col += 1

            if amount_cols and date_col:
                try:
                    df_ts = kpi_engine.get_time_series(table, amount_cols[0], date_col)
                    if not df_ts.empty:
                        fig = create_line_chart(df_ts, "periodo", "total", title=f"Tendencia - {table}")
                        self.chart_trend.set_figure(fig)
                        self.charts_export.append((f"Tendencia {table}", fig))
                except Exception:
                    pass

            if cat_col and amount_cols:
                try:
                    df_cat = kpi_engine.get_category_breakdown(table, amount_cols[0], cat_col)
                    if not df_cat.empty:
                        fig = create_bar_chart(df_cat, "categoria", "total", title=f"Por Categoria - {table}")
                        self.chart_category.set_figure(fig)
                        self.charts_export.append((f"Categorias {table}", fig))
                        self.data_table.set_data(df_cat)
                except Exception:
                    pass

        self.status_var.set("Atualizado")
