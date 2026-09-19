import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class KPICard(ttk.Frame):
    def __init__(self, parent, label, value, change=None, bootstyle="info", **kwargs):
        super().__init__(parent, padding=12, **kwargs)
        self/bootstyle = bootstyle

        top_row = ttk.Frame(self)
        top_row.pack(fill=X)

        self.value_label = ttk.Label(
            top_row, text=str(value),
            font=("Segoe UI", 22, "bold"),
            bootstyle=bootstyle,
        )
        self.value_label.pack(side=LEFT)

        if change is not None:
            style = "success" if change >= 0 else "danger"
            chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            self.change_label = ttk.Label(
                top_row, text=chg_text,
                font=("Segoe UI", 9, "bold"),
                bootstyle=style,
            )
            self.change_label.pack(side=RIGHT)

        self.label_widget = ttk.Label(
            self, text=label, font=("Segoe UI", 9),
        )
        self.label_widget.pack(anchor=W, pady=(4, 0))

    def update_value(self, value, change=None):
        self.value_label.configure(text=str(value))
        if change is not None and hasattr(self, "change_label"):
            style = "success" if change >= 0 else "danger"
            chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            self.change_label.configure(text=chg_text, bootstyle=style)


class MiniSparkline(ttk.Frame):
    def __init__(self, parent, data, color="#00d4ff", **kwargs):
        super().__init__(parent, **kwargs)
        fig = Figure(figsize=(2.5, 0.8), dpi=80)
        fig.patch.set_facecolor("#1a1f2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1a1f2e")
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
