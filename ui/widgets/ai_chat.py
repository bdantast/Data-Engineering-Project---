import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
from config import COLORS


class AIChatWidget(ttk.Frame):
    def __init__(self, parent, on_send=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style="Card.TFrame")
        self.on_send = on_send
        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self, style="Card.TFrame")
        header.pack(fill=X, pady=(0, 5))
        ttk.Label(
            header, text="Analise com IA", font=("Segoe UI", 12, "bold"),
            foreground=COLORS["neon_purple"], background=COLORS["bg_card"],
        ).pack(side=LEFT)
        self.status_label = ttk.Label(
            header, text="Pronto", font=("Segoe UI", 9),
            foreground=COLORS["text_muted"], background=COLORS["bg_card"],
        )
        self.status_label.pack(side=RIGHT)

        self.chat_display = ttk.ScrolledText(
            self, height=15, state=DISABLED, font=("Consolas", 10),
            wrap=WORD, bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"], relief="flat",
        )
        self.chat_display.pack(fill=BOTH, expand=True, pady=(0, 5))

        input_frame = ttk.Frame(self, style="Card.TFrame")
        input_frame.pack(fill=X)

        self.input_entry = ttk.Text(
            input_frame, height=2, font=("Segoe UI", 10), wrap=WORD,
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"], relief="flat",
        )
        self.input_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        self.send_btn = ttk.Button(
            input_frame, text="Enviar", bootstyle="info",
            command=self._on_send_click, width=10,
        )
        self.send_btn.pack(side=RIGHT)

        self.input_entry.bind("<Control-Return>", lambda e: self._on_send_click())
        self.input_entry.bind("<Return>", lambda e: self._on_send_click())

    def _on_send_click(self):
        text = self.input_entry.get("1.0", END).strip()
        if not text:
            return
        self.add_message("Voce", text, "user")
        self.input_entry.delete("1.0", END)
        self.set_status("Processando...")
        self.send_btn.configure(state=DISABLED)
        threading.Thread(target=self._send_async, args=(text,), daemon=True).start()

    def _send_async(self, text):
        try:
            if self.on_send:
                response = self.on_send(text)
                self.after(0, lambda: self.add_message("Data Engineering IA", response, "ai"))
        except Exception as e:
            self.after(0, lambda: self.add_message("Erro", str(e), "error"))
        finally:
            self.after(0, self._send_complete)

    def _send_complete(self):
        self.send_btn.configure(state=NORMAL)
        self.set_status("Pronto")

    def add_message(self, sender, message, msg_type="user"):
        self.chat_display.configure(state=NORMAL)
        tag_map = {
            "user": COLORS["neon_blue"],
            "ai": COLORS["neon_green"],
            "error": COLORS["danger"],
        }
        color = tag_map.get(msg_type, COLORS["text_primary"])
        self.chat_display.insert(END, f"{sender}: ", (f"_{color}",))
        self.chat_display.insert(END, f"{message}\n\n")
        self.chat_display.configure(state=DISABLED)
        self.chat_display.see(END)

    def set_status(self, text):
        self.status_label.configure(text=text)

    def clear(self):
        self.chat_display.configure(state=NORMAL)
        self.chat_display.delete("1.0", END)
        self.chat_display.configure(state=DISABLED)
