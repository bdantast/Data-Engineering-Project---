import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from config import COLORS


class ChartFrame(ttk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, padding=5, **kwargs)
        self.configure(style="Card.TFrame")
        self.title = title
        self.canvas_widget = None
        self._build_ui()

    def _build_ui(self):
        if self.title:
            header = ttk.Frame(self, style="Card.TFrame")
            header.pack(fill=X, pady=(0, 5))
            ttk.Label(
                header, text=self.title, font=("Segoe UI", 11, "bold"),
                foreground=COLORS["neon_blue"], background=COLORS["bg_card"],
            ).pack(side=LEFT)
        self.chart_container = ttk.Frame(self, style="Card.TFrame")
        self.chart_container.pack(fill=BOTH, expand=True)

    def set_figure(self, fig):
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.canvas_widget.draw()
        widget = self.canvas_widget.get_tk_widget()
        widget.configure(bg=COLORS["bg_card"])
        widget.pack(fill=BOTH, expand=True)

    def clear(self):
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None


class InteractiveChartFrame(ChartFrame):
    def __init__(self, parent, title="", show_toolbar=True, **kwargs):
        super().__init__(parent, title=title, **kwargs)
        self.show_toolbar = show_toolbar
        self.toolbar_widget = None

    def set_figure(self, fig):
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        if self.toolbar_widget:
            self.toolbar_widget.destroy()

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.canvas_widget.draw()
        widget = self.canvas_widget.get_tk_widget()
        widget.configure(bg=COLORS["bg_card"])
        widget.pack(fill=BOTH, expand=True)

        if self.show_toolbar:
            self.toolbar_widget = NavigationToolbar2Tk(self.canvas_widget, self.chart_container)
            self.toolbar_widget.update()
