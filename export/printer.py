import subprocess
import sys
import os
import tempfile


class Printer:
    @staticmethod
    def print_file(filepath):
        filepath = os.path.abspath(filepath)
        if sys.platform == "win32":
            os.startfile(filepath, "print")
            return True
        elif sys.platform == "darwin":
            subprocess.run(["lpr", filepath], check=True)
            return True
        else:
            subprocess.run(["lp", filepath], check=True)
            return True

    @staticmethod
    def print_text(text, title="Data Engineering"):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #1a237e; border-bottom: 2px solid #1a237e; padding-bottom: 10px; }}
                pre {{ white-space: pre-wrap; font-size: 12px; line-height: 1.6; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <pre>{text}</pre>
        </body>
        </html>
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(html)
            tmp_path = f.name
        try:
            Printer.print_file(tmp_path)
            return True
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    @staticmethod
    def print_pdf(filepath):
        if filepath.lower().endswith(".pdf"):
            return Printer.print_file(filepath)
        raise ValueError("Arquivo nao e PDF")


printer = Printer()
