import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from config import COLORS


class DataTable(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style="Card.TFrame")
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self, style="Card.TFrame")
        container.pack(fill=BOTH, expand=True)

        self.tree = ttk.Treeview(
            container, show="headings", selectmode="browse", height=15,
        )

        scrollbar_y = ttk.Scrollbar(container, orient=VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(self, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        scrollbar_x.pack(fill=X)

    def set_data(self, df, max_rows=500):
        self.tree.delete(*self.tree.get_children())
        if df is None or df.empty:
            return

        columns = list(df.columns)
        self.tree["columns"] = columns

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title(), anchor=W)
            max_width = max(
                len(str(col)) * 10,
                df[col].astype(str).str.len().max() * 8 if len(df) > 0 else 80,
            )
            self.tree.column(col, width=min(max_width, 200), anchor=W)

        for idx, (_, row) in enumerate(df.head(max_rows).iterrows()):
            values = [str(v) if pd.notna(v) else "" for v in row]
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", END, values=values, tags=(tag,))

        self.tree.tag_configure("even", background=COLORS["bg_table"])
        self.tree.tag_configure("odd", background=COLORS["bg_table_alt"])

    def set_dict_data(self, data_list, max_rows=500):
        self.tree.delete(*self.tree.get_children())
        if not data_list:
            return

        columns = list(data_list[0].keys())
        self.tree["columns"] = columns

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title(), anchor=W)
            self.tree.column(col, width=150, anchor=W)

        for idx, row in enumerate(data_list[:max_rows]):
            values = [str(row.get(c, "")) for c in columns]
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", END, values=values, tags=(tag,))

        self.tree.tag_configure("even", background=COLORS["bg_table"])
        self.tree.tag_configure("odd", background=COLORS["bg_table_alt"])

    def clear(self):
        self.tree.delete(*self.tree.get_children())
