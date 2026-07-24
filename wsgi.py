"""Entrypoint WSGI para produção (Vercel, Gunicorn, etc).
A Vercel detecta automaticamente uma variável `app` do tipo WSGI/ASGI em
arquivos como wsgi.py, app.py, main.py ou server.py — não precisa de config extra.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "production"))
