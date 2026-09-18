import webbrowser
import urllib.parse
from datetime import datetime


class ShareManager:
    @staticmethod
    def share_whatsapp(message, phone=None):
        if phone:
            phone = phone.replace("+", "").replace("-", "").replace(" ", "")
            url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"
        else:
            url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(message)}"
        webbrowser.open(url)
        return url

    @staticmethod
    def share_telegram(message, chat_id=None):
        if chat_id:
            url = f"https://t.me/share/url?url=&text={urllib.parse.quote(message)}"
        else:
            url = f"https://t.me/share/url?text={urllib.parse.quote(message)}"
        webbrowser.open(url)
        return url

    @staticmethod
    def share_email(to_email, subject, body):
        mailto_url = (
            f"mailto:{to_email}"
            f"?subject={urllib.parse.quote(subject)}"
            f"&body={urllib.parse.quote(body)}"
        )
        webbrowser.open(mailto_url)
        return mailto_url

    @staticmethod
    def generate_summary_message(kpis, table_name=""):
        lines = [
            f"Data Engineering - Resumo {table_name}",
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
        ]
        for key, val in kpis.items():
            if isinstance(val, (int, float)) and not key.startswith("colunas"):
                label = key.replace("_", " ").title()
                lines.append(f"{label}: {val:,.2f}" if isinstance(val, float) else f"{label}: {val}")
        return "\n".join(lines)

    @staticmethod
    def generate_ai_summary_message(ai_analysis, table_name=""):
        preview = ai_analysis[:500] + "..." if len(ai_analysis) > 500 else ai_analysis
        return (
            f"Data Engineering - Analise IA {table_name}\n"
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"{preview}"
        )


share_manager = ShareManager()
