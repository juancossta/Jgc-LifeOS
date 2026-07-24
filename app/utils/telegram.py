import requests
from flask import current_app


def enviar_telegram(chat_id, texto):
    """Envia uma mensagem de texto via Telegram Bot API.
    Retorna (ok: bool, detalhe: str)."""
    token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return False, "TELEGRAM_BOT_TOKEN não configurado no servidor."
    if not chat_id:
        return False, "Chat ID do Telegram não configurado no seu perfil."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": texto}, timeout=10)
        if resp.status_code == 200 and resp.json().get("ok"):
            return True, "Mensagem enviada."
        return False, f"Telegram retornou erro: {resp.text}"
    except requests.RequestException as exc:
        return False, f"Falha de conexão com o Telegram: {exc}"
