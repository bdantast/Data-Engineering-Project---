import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class KPICard(ttk.Frame):
    def __init__(self, parent, label, value, change=None, bootstyle="primary", **kwargs):
        super().__init__(parent, padding=10, **kwargs)

        self.configure(bootstyle="light")

        value_frame = ttk.Frame(self)
        value_frame.pack(fill=X)

        self.value_label = ttk.Label(
            value_frame,
            text=str(value),
            font=("Segoe UI", 20, "bold"),
            bootstyle=bootstyle,
        )
        self.value_label.pack(anchor=W)

        self.label_widget = ttk.Label(
            self,
            text=label,
            font=("Segoe UI", 9),
            bootstyle="secondary",
        )
        self.label_widget.pack(anchor=W, pady=(2, 0))

        if change is not None:
            chg_color = "success" if change >= 0 else "danger"
            chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            self.change_label = ttk.Label(
                self,
                text=chg_text,
                font=("Segoe UI", 9, "bold"),
                bootstyle=chg_color,
            )
            self.change_label.pack(anchor=W, pady=(2, 0))

    def update_value(self, value, change=None):
        self.value_label.configure(text=str(value))
        if change is not None and hasattr(self, "change_label"):
            chg_color = "success" if change >= 0 else "danger"
            chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            self.change_label.configure(text=chg_text, bootstyle=chg_color)
