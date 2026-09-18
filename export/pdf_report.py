import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from core.charts import fig_to_image_bytes


class PDFReport:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            "ReportTitle",
            parent=self.styles["Heading1"],
            fontSize=22,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor("#1a237e"),
        ))
        self.styles.add(ParagraphStyle(
            "ReportSubtitle",
            parent=self.styles["Heading2"],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor("#455a64"),
        ))
        self.styles.add(ParagraphStyle(
            "KPILabel",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#666666"),
        ))
        self.styles.add(ParagraphStyle(
            "KPIValue",
            parent=self.styles["Normal"],
            fontSize=16,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1a237e"),
        ))

    def generate(self, output_path, data, charts=None, ai_analysis=""):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        story = []
        story.extend(self._build_header())
        story.extend(self._build_kpi_section(data.get("kpis", {})))
        if charts:
            story.extend(self._build_charts_section(charts))
        if ai_analysis:
            story.extend(self._build_analysis_section(ai_analysis))
        story.extend(self._build_footer())
        doc.build(story)
        return output_path

    def _build_header(self):
        elements = []
        elements.append(Spacer(1, 2 * cm))
        elements.append(Paragraph("DataPulse - Relatorio de Analise", self.styles["ReportTitle"]))
        elements.append(Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}",
            self.styles["ReportSubtitle"],
        ))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
        elements.append(Spacer(1, 1 * cm))
        return elements

    def _build_kpi_section(self, kpis):
        elements = []
        elements.append(Paragraph("KPIs Principais", self.styles["Heading2"]))
        elements.append(Spacer(1, 0.5 * cm))
        flat_kpis = {}
        for table_data in kpis.values():
            for category in ["vendas", "financeiro", "resumo"]:
                cat_data = table_data.get(category, {})
                for key, val in cat_data.items():
                    if isinstance(val, (int, float)) and not key.startswith("colunas"):
                        flat_kpis[key] = val
        if flat_kpis:
            table_data = [["Metrica", "Valor"]]
            for key, val in list(flat_kpis.items())[:15]:
                label = key.replace("_", " ").title()
                if isinstance(val, float):
                    formatted = f"{val:,.2f}"
                else:
                    formatted = str(val)
                table_data.append([label, formatted])
            table = Table(table_data, colWidths=[12 * cm, 6 * cm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
                ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]))
            elements.append(table)
        elements.append(Spacer(1, 1 * cm))
        return elements

    def _build_charts_section(self, charts):
        elements = []
        elements.append(PageBreak())
        elements.append(Paragraph("Graficos", self.styles["Heading2"]))
        elements.append(Spacer(1, 0.5 * cm))
        for i, (title, fig) in enumerate(charts):
            elements.append(Paragraph(title, self.styles["Heading3"]))
            img_buf = fig_to_image_bytes(fig)
            img = Image(img_buf, width=16 * cm, height=9 * cm)
            elements.append(img)
            elements.append(Spacer(1, 0.5 * cm))
            if (i + 1) % 2 == 0 and i < len(charts) - 1:
                elements.append(PageBreak())
        return elements

    def _build_analysis_section(self, analysis_text):
        elements = []
        elements.append(PageBreak())
        elements.append(Paragraph("Analise por Inteligencia Artificial", self.styles["Heading2"]))
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))
        elements.append(Spacer(1, 0.5 * cm))
        for line in analysis_text.split("\n"):
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 0.3 * cm))
                continue
            if line.startswith("# "):
                elements.append(Paragraph(line[2:], self.styles["Heading1"]))
            elif line.startswith("## "):
                elements.append(Paragraph(line[3:], self.styles["Heading2"]))
            elif line.startswith("### "):
                elements.append(Paragraph(line[4:], self.styles["Heading3"]))
            elif line.startswith("- "):
                elements.append(Paragraph(f"&bull; {line[2:]}", self.styles["Normal"]))
            else:
                clean = line.replace("**", "<b>").replace("**", "</b>")
                elements.append(Paragraph(clean, self.styles["Normal"]))
        return elements

    def _build_footer(self):
        elements = []
        elements.append(Spacer(1, 2 * cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))
        elements.append(Paragraph(
            f"DataPulse Business Intelligence - Relatorio gerado automaticamente - {datetime.now().strftime('%d/%m/%Y')}",
            ParagraphStyle("Footer", parent=self.styles["Normal"], fontSize=8,
                           alignment=TA_CENTER, textColor=colors.HexColor("#999999")),
        ))
        return elements


pdf_report = PDFReport()
