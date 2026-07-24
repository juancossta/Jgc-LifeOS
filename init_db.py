"""Script auxiliar: cria o banco (create_all) para desenvolvimento rápido sem migrations."""
from dotenv import load_dotenv

load_dotenv()  # lê o .env — essencial para pegar o DATABASE_URL do Supabase

from app import create_app
from app.extensions import db

app = create_app("development")
with app.app_context():
    db.create_all()
    print("Banco de dados criado/atualizado com sucesso.")
    print("URI usada:", app.config["SQLALCHEMY_DATABASE_URI"].split("@")[-1] if "@" in app.config["SQLALCHEMY_DATABASE_URI"] else app.config["SQLALCHEMY_DATABASE_URI"])
