import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from ui.pages.dashboard import DashboardPage
from ui.pages.vendas import VendasPage
from ui.pages.financeiro import FinanceiroPage
from ui.pages.ai_analysis import AIAnalysisPage
from ui.pages.export import ExportPage
from ui.pages.settings import SettingsPage
from config import APP_NAME, APP_VERSION, COLORS


class App:
    def __init__(self):
        self.style = Style(theme="darkly")
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

        self.pages = {}
        self.current_page = None
        self._build_ui()

    def _build_ui(self):
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        logo_frame = ttk.Frame(self.sidebar)
        logo_frame.pack(fill=X, pady=(25, 25), padx=15)
        ttk.Label(
            logo_frame, text="Data Enginee",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor=W)
        ttk.Label(
            logo_frame, text="Business Intelligence",
            font=("Segoe UI", 8),
        ).pack(anchor=W, pady=(2, 0))

        ttk.Separator(self.sidebar).pack(fill=X, padx=15, pady=(0, 20))

        nav_items = [
            ("Dashboard", "dashboard"),
            ("Vendas", "vendas"),
            ("Financeiro", "financeiro"),
            ("Analise IA", "ai_analysis"),
            ("Exportar", "export"),
            ("Configuracoes", "settings"),
        ]

        self.nav_buttons = {}
        for label, key in nav_items:
            btn = ttk.Button(
                self.sidebar,
                text=f"  {label}",
                bootstyle="info-outline",
                command=lambda k=key: self._show_page(k),
            )
            btn.pack(fill=X, padx=12, pady=4)
            self.nav_buttons[key] = (btn, label)

        ttk.Frame(self.sidebar).pack(fill=Y, expand=True)
        ttk.Label(
            self.sidebar, text=f"v{APP_VERSION}",
            font=("Segoe UI", 8),
        ).pack(side=BOTTOM, pady=10)

        self.content = ttk.Frame(self.root)
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

        for btn_key, (btn, label) in self.nav_buttons.items():
            if btn_key == key:
                btn.configure(bootstyle="info")
            else:
                btn.configure(bootstyle="info-outline")

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
