import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from ui.pages.dashboard import DashboardPage
from ui.pages.vendas import VendasPage
from ui.pages.financeiro import FinanceiroPage
from ui.pages.ai_analysis import AIAnalysisPage
from ui.pages.export import ExportPage
from ui.pages.settings import SettingsPage
from config import APP_NAME, APP_VERSION, APP_THEME, COLORS


class App:
    def __init__(self):
        self.style = Style(theme=APP_THEME)
        self.root = self.style.master
        self.root.title(f"{APP_NAME} v{APP_VERSION} - Business Intelligence")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 600)
        self.root.update_idletasks()
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        x = (w - 1280) // 2
        y = (h - 800) // 2
        self.root.geometry(f"1280x800+{x}+{y}")
        self.root.configure(bg=COLORS["bg_dark"])
        self._setup_custom_theme()
        self.pages = {}
        self.current_page = None
        self._build_ui()

    def _setup_custom_theme(self):
        self.style.configure(".", background=COLORS["bg_dark"], foreground=COLORS["text_primary"])
        self.style.configure("TFrame", background=COLORS["bg_dark"])
        self.style.configure("Card.TFrame", background=COLORS["bg_card"], relief="flat")
        self.style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_primary"])
        self.style.configure("Card.TLabel", background=COLORS["bg_card"])
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLORS["text_primary"])
        self.style.configure("KPI.TLabel", font=("Segoe UI", 22, "bold"), foreground=COLORS["neon_blue"])
        self.style.configure("KPILabel.TLabel", font=("Segoe UI", 9), foreground=COLORS["text_secondary"])
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("Nav.TButton", font=("Segoe UI", 11), padding=(15, 12))
        self.style.configure("Treeview", background=COLORS["bg_table"], foreground=COLORS["text_primary"],
                             fieldbackground=COLORS["bg_table"], font=("Segoe UI", 9), rowheight=28)
        self.style.configure("Treeview.Heading", background=COLORS["bg_card"], foreground=COLORS["neon_blue"],
                             font=("Segoe UI", 9, "bold"), relief="flat")
        self.style.map("Treeview", background=[("selected", COLORS["neon_blue"])],
                        foreground=[("selected", COLORS["bg_dark"])])
        self.style.configure("TEntry", fieldbackground=COLORS["bg_card"], foreground=COLORS["text_primary"],
                             insertcolor=COLORS["text_primary"])
        self.style.configure("TLabelframe", background=COLORS["bg_card"], foreground=COLORS["neon_blue"])
        self.style.configure("TLabelframe.Label", background=COLORS["bg_card"], foreground=COLORS["neon_blue"],
                             font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        self.sidebar = ttk.Frame(self.root, width=200, style="Card.TFrame")
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        logo_frame = ttk.Frame(self.sidebar, style="Card.TFrame")
        logo_frame.pack(fill=X, pady=(25, 25), padx=15)
        ttk.Label(
            logo_frame, text="Data Enginee", font=("Segoe UI", 14, "bold"),
            foreground=COLORS["text_primary"], background=COLORS["bg_card"],
        ).pack(anchor=W)
        ttk.Label(
            logo_frame, text="Business Intelligence", font=("Segoe UI", 8),
            foreground=COLORS["text_muted"], background=COLORS["bg_card"],
        ).pack(anchor=W, pady=(2, 0))

        ttk.Frame(self.sidebar, height=1, background=COLORS["border"]).pack(fill=X, padx=15, pady=(0, 20))

        nav_items = [
            ("Dashboard", "dashboard", COLORS["neon_blue"]),
            ("Vendas", "vendas", COLORS["neon_green"]),
            ("Financeiro", "financeiro", COLORS["neon_orange"]),
            ("Analise IA", "ai_analysis", COLORS["neon_purple"]),
            ("Exportar", "export", COLORS["neon_pink"]),
            ("Configuracoes", "settings", COLORS["text_muted"]),
        ]

        self.nav_buttons = {}
        for label, key, color in nav_items:
            btn = ttk.Button(
                self.sidebar, text=f"  {label}", style="Nav.TButton",
                command=lambda k=key: self._show_page(k),
            )
            btn.pack(fill=X, padx=12, pady=4)
            btn._nav_color = color
            btn._nav_label = label
            self.nav_buttons[key] = btn

        ttk.Frame(self.sidebar, style="Card.TFrame").pack(fill=Y, expand=True)
        ttk.Label(
            self.sidebar, text=f"v{APP_VERSION}", font=("Segoe UI", 8),
            foreground=COLORS["text_muted"], background=COLORS["bg_card"],
        ).pack(side=BOTTOM, pady=10)

        self.content = ttk.Frame(self.root, style="TFrame")
        self.content.pack(side=LEFT, fill=BOTH, expand=True)

        self._create_pages()
        self._show_page("dashboard")

    def _create_pages(self):
        page_classes = {
            "dashboard": DashboardPage,
            "vendas": VendasPage,
            "financeiro": FinanceiroPage,
            "ai_analysis": AIAnalysisPage,
            "export": ExportPage,
            "settings": SettingsPage,
        }
        for key, cls in page_classes.items():
            page = cls(self.content)
            self.pages[key] = page

    def _show_page(self, key):
        if self.current_page:
            self.pages[self.current_page].pack_forget()

        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.configure(bootstyle="info")
            else:
                btn.configure(bootstyle="dark")

        self.pages[key].pack(fill=BOTH, expand=True)
        self.current_page = key

        if key == "dashboard" and hasattr(self.pages[key], "load_data"):
            self.pages[key].load_data()

    def run(self):
        self.root.mainloop()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
