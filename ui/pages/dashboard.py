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


class DashboardPage(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style="TFrame")
        self.kpi_cards = {}
        self.charts = []
        self._build_ui()

    def _build_ui(self):
        canvas = ttk.Canvas(self, highlightthickness=False, bg=COLORS["bg_dark"])
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style="TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.main_frame = self.scrollable_frame

        header = ttk.Frame(self.main_frame, style="TFrame")
        header.pack(fill=X, padx=20, pady=(20, 10))
        ttk.Label(
            header, text="Dashboard - Visao Geral",
            font=("Segoe UI", 18, "bold"),
            foreground=COLORS["text_primary"], background=COLORS["bg_dark"],
        ).pack(side=LEFT)

        self.refresh_btn = ttk.Button(
            header, text="Atualizar", bootstyle="info-outline",
            command=self.load_data, width=12,
        )
        self.refresh_btn.pack(side=RIGHT)

        self.kpi_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.kpi_frame.pack(fill=X, padx=20, pady=10)

        charts_row = ttk.Frame(self.main_frame, style="TFrame")
        charts_row.pack(fill=X, padx=20, pady=5)

        self.chart1 = ChartFrame(charts_row, title="Tendencia")
        self.chart1.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        self.chart2 = ChartFrame(charts_row, title="Distribuicao")
        self.chart2.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))

        self.table_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.table_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        ttk.Label(
            self.table_frame, text="Dados Recentes",
            font=("Segoe UI", 12, "bold"),
            foreground=COLORS["neon_blue"], background=COLORS["bg_dark"],
        ).pack(anchor=W, pady=(0, 8))
        self.data_table = DataTable(self.table_frame)
        self.data_table.pack(fill=BOTH, expand=True)

        self.status_var = ttk.StringVar(value="Pronto")
        ttk.Label(
            self.main_frame, textvariable=self.status_var,
            font=("Segoe UI", 9),
            foreground=COLORS["text_muted"], background=COLORS["bg_dark"],
        ).pack(anchor=W, padx=20, pady=(5, 20))

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
                f"Atualizado - {len(schema_discover.tables)} tabelas encontradas"
            )
        except Exception as e:
            self.status_var.set(f"Erro ao atualizar: {e}")

    def _update_kpi_cards(self):
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()

        total_receita = 0
        total_registros = 0
        margem = 0
        media_valor = 0

        for table, kpis in kpi_engine.kpis.items():
            vendas = kpis.get("vendas", {})
            fin = kpis.get("financeiro", {})
            resumo = kpis.get("resumo", {})
            total_registros += resumo.get("total_registros", 0)
            margem = fin.get("margem_percentual", margem)
            for key, val in vendas.items():
                if key.endswith("_total") and isinstance(val, (int, float)):
                    total_receita += val
            amount_cols = vendas.get("colunas_valor", [])
            if amount_cols:
                media_val = vendas.get(f"{amount_cols[0]}_media", 0)
                media_valor += media_val

        cards_data = [
            ("Registros Total", f"{total_registros:,}", None, COLORS["neon_blue"]),
            ("Receita Total", f"R$ {total_receita:,.2f}", None, COLORS["neon_green"]),
            ("Margem %", f"{margem:.1f}%", None, COLORS["neon_purple"]),
            ("Media por Registro", f"R$ {media_valor:,.2f}", None, COLORS["neon_orange"]),
        ]

        for i, (label, value, change, color) in enumerate(cards_data):
            card = KPICard(self.kpi_frame, label=label, value=value, change=change, color=color)
            card.grid(row=0, column=i, padx=8, pady=5, sticky=NSEW)
            self.kpi_frame.columnconfigure(i, weight=1)
            self.kpi_cards[label] = card

    def _update_charts(self):
        for table, kpis in kpi_engine.kpis.items():
            vendas = kpis.get("vendas", {})
            top_cats = vendas.get("top_categorias", [])
            amount_cols = vendas.get("colunas_valor", [])
            date_col = vendas.get("coluna_data")
            cat_col = vendas.get("coluna_categoria")

            if top_cats and len(top_cats) > 1:
                df_cats = pd.DataFrame(top_cats)
                if "categoria" in df_cats.columns and "total" in df_cats.columns:
                    fig = create_pie_chart(
                        df_cats.head(8), "categoria", "total",
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
