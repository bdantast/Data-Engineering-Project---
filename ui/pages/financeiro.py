import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import pandas as pd
from ui.widgets.kpi_card import KPICard
from ui.widgets.chart_frame import InteractiveChartFrame
from ui.widgets.data_table import DataTable
from core.schema_discover import schema_discover
from core.kpi_engine import kpi_engine
from core.charts import create_bar_chart, create_pie_chart, create_line_chart


class FinanceiroPage(ttk.Frame):
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
        ttk.Label(header, text="Analise Financeira", font=("Segoe UI", 16, "bold")).pack(side=LEFT)
        ttk.Button(header, text="Atualizar", bootstyle="info-outline",
                   command=self.load_data, width=12).pack(side=RIGHT)

        self.kpi_frame = ttk.Frame(self.scrollable)
        self.kpi_frame.pack(fill=X, padx=15, pady=5)

        charts_row = ttk.Frame(self.scrollable)
        charts_row.pack(fill=X, padx=15, pady=5)
        self.chart_lucro = InteractiveChartFrame(charts_row, title="Composicao Financeira")
        self.chart_lucro.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        self.chart_margem = InteractiveChartFrame(charts_row, title="Margens")
        self.chart_margem.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))

        self.table_frame = ttk.Frame(self.scrollable)
        self.table_frame.pack(fill=BOTH, expand=True, padx=15, pady=5)
        ttk.Label(self.table_frame, text="Detalhamento Financeiro", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(0, 5))
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
            fin = kpis.get("financeiro", {})
            receita = fin.get("receita_total", 0)
            custo = fin.get("custo_total", 0)
            lucro = fin.get("lucro", 0)
            margem = fin.get("margem_percentual", 0)

            kpis_data = [
                ("Receita", f"R$ {receita:,.2f}", "success"),
                ("Custos", f"R$ {custo:,.2f}", "danger"),
                ("Lucro", f"R$ {lucro:,.2f}", "primary"),
                ("Margem", f"{margem:.1f}%", "info"),
            ]
            for label, value, style in kpis_data:
                card = KPICard(self.kpi_frame, label=label, value=value, bootstyle=style)
                card.grid(row=0, column=col, padx=5, pady=5, sticky=NSEW)
                self.kpi_frame.columnconfigure(col, weight=1)
                col += 1

            if receita > 0 or custo > 0:
                df_comp = pd.DataFrame({
                    "categoria": ["Receita", "Custos", "Lucro"],
                    "valor": [receita, custo, lucro],
                })
                fig = create_pie_chart(df_comp, "categoria", "valor", title=f"Composicao - {table}")
                self.chart_lucro.set_figure(fig)
                self.charts_export.append((f"Composicao {table}", fig))

            if margem > 0:
                df_margem = pd.DataFrame({
                    "metrica": ["Margem Atual", "Margem Restante"],
                    "valor": [margem, 100 - margem],
                })
                fig = create_bar_chart(df_margem, "metrica", "valor", title="Margem (%)")
                self.chart_margem.set_figure(fig)
                self.charts_export.append((f"Margem {table}", fig))

            vendas = kpis.get("vendas", {})
            amount_cols = vendas.get("colunas_valor", [])
            date_col = vendas.get("coluna_data")
            if amount_cols and date_col:
                try:
                    df_ts = kpi_engine.get_time_series(table, amount_cols[0], date_col)
                    if not df_ts.empty:
                        df_detail = pd.DataFrame({
                            "Receita": [receita],
                            "Custos": [custo],
                            "Lucro": [lucro],
                            "Margem %": [margem],
                        })
                        self.data_table.set_data(df_detail)
                except Exception:
                    pass

        self.status_var.set("Atualizado")
