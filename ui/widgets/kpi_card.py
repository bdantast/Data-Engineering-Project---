import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import COLORS
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker


class KPICard(ttk.Frame):
    def __init__(self, parent, label, value, change=None, color=COLORS["neon_blue"], **kwargs):
        super().__init__(parent, padding=12, **kwargs)
        self.configure(style="Card.TFrame")

        self.color = color

        top_row = ttk.Frame(self, style="Card.TFrame")
        top_row.pack(fill=X)

        self.value_label = ttk.Label(
            top_row, text=str(value), font=("Segoe UI", 22, "bold"),
            foreground=color, background=COLORS["bg_card"],
        )
        self.value_label.pack(side=LEFT)

        if change is not None:
            chg_color = COLORS["success"] if change >= 0 else COLORS["danger"]
            chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            self.change_label = ttk.Label(
                top_row, text=chg_text, font=("Segoe UI", 9, "bold"),
                foreground=chg_color, background=COLORS["bg_card"],
            )
            self.change_label.pack(side=RIGHT)

        self.label_widget = ttk.Label(
            self, text=label, font=("Segoe UI", 9),
            foreground=COLORS["text_secondary"], background=COLORS["bg_card"],
        )
        self.label_widget.pack(anchor=W, pady=(4, 0))

    def update_value(self, value, change=None):
        self.value_label.configure(text=str(value))
        if change is not None and hasattr(self, "change_label"):
            chg_color = COLORS["success"] if change >= 0 else COLORS["danger"]
            chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            self.change_label.configure(text=chg_text, foreground=chg_color)


class MiniSparkline(ttk.Frame):
    def __init__(self, parent, data, color=COLORS["neon_blue"], **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style="Card.TFrame")
        fig = Figure(figsize=(2.5, 0.8), dpi=80)
        fig.patch.set_facecolor(COLORS["bg_card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["bg_card"])
        ax.plot(data, color=color, linewidth=2)
        ax.fill_between(range(len(data)), data, alpha=0.15, color=color)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
