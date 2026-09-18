import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import os
import tempfile
from tkinter import filedialog, messagebox
from core.schema_discover import schema_discover
from core.kpi_engine import kpi_engine
from core.database import db
from core.charts import create_bar_chart, create_pie_chart, create_line_chart
from export.pdf_report import pdf_report
from export.excel_report import excel_report
from export.email_sender import email_sender
from export.share import share_manager
from export.printer import printer


class ExportPage(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill=X, padx=15, pady=(15, 10))
        ttk.Label(header, text="Exportar e Compartilhar", font=("Segoe UI", 16, "bold")).pack(side=LEFT)

        export_frame = ttk.LabelFrame(self, text="Exportacao", padding=15)
        export_frame.pack(fill=X, padx=15, pady=5)

        pdf_row = ttk.Frame(export_frame)
        pdf_row.pack(fill=X, pady=3)
        ttk.Button(pdf_row, text="Gerar Relatorio PDF", bootstyle="danger",
                   command=self._export_pdf, width=25).pack(side=LEFT, padx=(0, 10))
        ttk.Label(pdf_row, text="Relatorio completo com graficos e KPIs", font=("Segoe UI", 9), bootstyle="secondary").pack(side=LEFT)

        excel_row = ttk.Frame(export_frame)
        excel_row.pack(fill=X, pady=3)
        ttk.Button(excel_row, text="Gerar Planilha Excel", bootstyle="success",
                   command=self._export_excel, width=25).pack(side=LEFT, padx=(0, 10))
        ttk.Label(excel_row, text="Dados brutos, KPIs e graficos em abas", font=("Segoe UI", 9), bootstyle="secondary").pack(side=LEFT)

        share_frame = ttk.LabelFrame(self, text="Compartilhar", padding=15)
        share_frame.pack(fill=X, padx=15, pady=5)

        email_row = ttk.Frame(share_frame)
        email_row.pack(fill=X, pady=3)
        ttk.Label(email_row, text="Email:", font=("Segoe UI", 10), width=8).pack(side=LEFT)
        self.email_entry = ttk.Entry(email_row, width=35)
        self.email_entry.pack(side=LEFT, padx=(0, 10))
        ttk.Button(email_row, text="Enviar Email", bootstyle="info",
                   command=self._send_email).pack(side=LEFT, padx=(0, 10))
        ttk.Button(email_row, text="Abrir Email", bootstyle="info-outline",
                   command=self._open_email).pack(side=LEFT)

        phone_row = ttk.Frame(share_frame)
        phone_row.pack(fill=X, pady=3)
        ttk.Label(phone_row, text="Telefone:", font=("Segoe UI", 10), width=8).pack(side=LEFT)
        self.phone_entry = ttk.Entry(phone_row, width=20)
        self.phone_entry.pack(side=LEFT, padx=(0, 10))
        ttk.Button(phone_row, text="WhatsApp", bootstyle="success-outline",
                   command=self._share_whatsapp).pack(side=LEFT, padx=5)
        ttk.Button(phone_row, text="Telegram", bootstyle="info-outline",
                   command=self._share_telegram).pack(side=LEFT, padx=5)

        print_frame = ttk.LabelFrame(self, text="Impressao", padding=15)
        print_frame.pack(fill=X, padx=15, pady=5)
        ttk.Button(print_frame, text="Imprimir Relatorio", bootstyle="secondary",
                   command=self._print_report, width=25).pack(side=LEFT)

        self.status_var = ttk.StringVar(value="Pronto")
        ttk.Label(self, textvariable=self.status_var, font=("Segoe UI", 9), bootstyle="secondary").pack(anchor=W, padx=15, pady=(5, 15))

    def _export_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Salvar Relatorio PDF",
        )
        if not path:
            return
        self.status_var.set("Gerando PDF...")
        threading.Thread(target=self._pdf_async, args=(path,), daemon=True).start()

    def _pdf_async(self, path):
        try:
            charts = []
            for table, kpis in kpi_engine.kpis.items():
                vendas = kpis.get("vendas", {})
                amount_cols = vendas.get("colunas_valor", [])
                date_col = vendas.get("coluna_data")
                cat_col = vendas.get("coluna_categoria")
                if amount_cols and date_col:
                    try:
                        df_ts = kpi_engine.get_time_series(table, amount_cols[0], date_col)
                        if not df_ts.empty:
                            fig = create_line_chart(df_ts, "periodo", "total", title=f"Tendencia {table}")
                            charts.append((f"Tendencia {table}", fig))
                    except Exception:
                        pass
                if cat_col and amount_cols:
                    try:
                        df_cat = kpi_engine.get_category_breakdown(table, amount_cols[0], cat_col)
                        if not df_cat.empty:
                            fig = create_pie_chart(df_cat, "categoria", "total", title=f"Distribuicao {table}")
                            charts.append((f"Distribuicao {table}", fig))
                    except Exception:
                        pass
            pdf_report.generate(path, {"kpis": kpi_engine.kpis}, charts)
            self.after(0, lambda: self.status_var.set(f"PDF salvo em: {path}"))
            self.after(0, lambda: messagebox.showinfo("Sucesso", f"PDF gerado:\n{path}"))
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Erro: {e}"))
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))

    def _export_excel(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            title="Salvar Planilha Excel",
        )
        if not path:
            return
        self.status_var.set("Gerando Excel...")
        threading.Thread(target=self._excel_async, args=(path,), daemon=True).start()

    def _excel_async(self, path):
        try:
            dataframes = {}
            for table in schema_discover.tables:
                try:
                    df = schema_discover.get_table_preview(table, limit=1000)
                    if not df.empty:
                        dataframes[table] = df
                except Exception:
                    pass
            excel_report.generate(path, dataframes=dataframes, ai_analysis="")
            self.after(0, lambda: self.status_var.set(f"Excel salvo em: {path}"))
            self.after(0, lambda: messagebox.showinfo("Sucesso", f"Excel gerado:\n{path}"))
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Erro: {e}"))
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))

    def _send_email(self):
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showwarning("Aviso", "Digite um email valido")
            return
        if not email_sender.is_configured():
            messagebox.showwarning("Aviso", "Email SMTP nao configurado. Configure no .env")
            return
        self.status_var.set("Enviando email...")
        threading.Thread(target=self._email_async, args=(email,), daemon=True).start()

    def _email_async(self, email):
        try:
            summary = share_manager.generate_summary_message(
                {t: kpis.get("resumo", {}) for t, kpis in kpi_engine.kpis.items()}
            )
            email_sender.send(
                to_email=email,
                subject="DataPulse - Relatorio de Analise",
                body=f"<pre>{summary}</pre>",
            )
            self.after(0, lambda: self.status_var.set("Email enviado com sucesso!"))
            self.after(0, lambda: messagebox.showinfo("Sucesso", "Email enviado!"))
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Erro: {e}"))
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))

    def _open_email(self):
        summary = share_manager.generate_summary_message(
            {t: kpis.get("resumo", {}) for t, kpis in kpi_engine.kpis.items()}
        )
        share_manager.share_email("", "DataPulse - Relatorio", summary)

    def _share_whatsapp(self):
        phone = self.phone_entry.get().strip()
        summary = share_manager.generate_summary_message(
            {t: kpis.get("resumo", {}) for t, kpis in kpi_engine.kpis.items()}
        )
        share_manager.share_whatsapp(summary, phone if phone else None)

    def _share_telegram(self):
        summary = share_manager.generate_summary_message(
            {t: kpis.get("resumo", {}) for t, kpis in kpi_engine.kpis.items()}
        )
        share_manager.share_telegram(summary)

    def _print_report(self):
        try:
            summary = share_manager.generate_summary_message(
                {t: kpis.get("resumo", {}) for t, kpis in kpi_engine.kpis.items()}
            )
            printer.print_text(summary)
            self.status_var.set("Enviado para impressao")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
