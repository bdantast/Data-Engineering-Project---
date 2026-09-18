import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.pages.dashboard import DashboardPage
from ui.pages.vendas import VendasPage
from ui.pages.financeiro import FinanceiroPage
from ui.pages.ai_analysis import AIAnalysisPage
from ui.pages.export import ExportPage
from ui.pages.settings import SettingsPage
from config import APP_NAME, APP_VERSION, APP_THEME


class App:
    def __init__(self):
        self.root = ttk.Window(
            title=f"{APP_NAME} v{APP_VERSION} - Business Intelligence",
            themename=APP_THEME,
            size=(1280, 800),
            minsize=(1024, 600),
        )
        self.root.place_window_center()
        self.pages = {}
        self.current_page = None
        self._build_ui()

    def _build_ui(self):
        self.sidebar = ttk.Frame(self.root, width=220, bootstyle="dark")
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        logo_frame = ttk.Frame(self.sidebar, bootstyle="dark")
        logo_frame.pack(fill=X, pady=(20, 30), padx=15)
        ttk.Label(
            logo_frame,
            text=APP_NAME,
            font=("Segoe UI", 18, "bold"),
            bootstyle="inverse-primary",
        ).pack(anchor=W)
        ttk.Label(
            logo_frame,
            text="Business Intelligence",
            font=("Segoe UI", 9),
            bootstyle="inverse-secondary",
        ).pack(anchor=W)

        nav_items = [
            ("Dashboard", "dashboard", "primary"),
            ("Vendas", "vendas", "success"),
            ("Financeiro", "financeiro", "warning"),
            ("Analise IA", "ai_analysis", "info"),
            ("Exportar", "export", "danger"),
            ("Configuracoes", "settings", "secondary"),
        ]

        self.nav_buttons = {}
        for label, key, style in nav_items:
            btn = ttk.Button(
                self.sidebar,
                text=f"  {label}",
                bootstyle=f"{style}-outline",
                command=lambda k=key: self._show_page(k),
                width=20,
            )
            btn._base_style = style
            btn.pack(fill=X, padx=10, pady=3)
            self.nav_buttons[key] = btn

        ttk.Frame(self.sidebar).pack(fill=Y, expand=True)

        version_label = ttk.Label(
            self.sidebar,
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 8),
            bootstyle="inverse-secondary",
        )
        version_label.pack(side=BOTTOM, pady=10)

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

        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.configure(bootstyle=btn._base_style)
            else:
                btn.configure(bootstyle=f"{btn._base_style}-outline")

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
