import os
from datetime import timedelta
from sqlalchemy.pool import NullPool

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    WTF_CSRF_TIME_LIMIT = None

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            # Compatibilidade com URLs antigas do Heroku/Render
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        if database_url.startswith("postgresql://"):
            # Força o driver psycopg3 (pacote "psycopg"), já que o SQLAlchemy usa
            # psycopg2 por padrão quando o esquema é só "postgresql://". Usamos
            # psycopg3 porque ele tem wheels prontos para versões novas do Python
            # (psycopg2-binary costuma demorar a suportar Python recém-lançado).
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or (
        "sqlite:///" + os.path.join(basedir, "instance", "lifeos.db")
    )

    # Notificações via Telegram
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    # Segredo exigido como query param (?secret=...) para autorizar o endpoint de cron
    CRON_SECRET = os.environ.get("CRON_SECRET", "")
    TIMEZONE = os.environ.get("TIMEZONE", "America/Sao_Paulo")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Em serverless (Vercel), cada invocação é um processo isolado — o pooling de
    # conexões da própria aplicação não ajuda e ainda conflita com o pooler do
    # Supabase (PgBouncer em modo transaction, porta 6543). NullPool evita que o
    # SQLAlchemy mantenha um pool próprio por cima do pooler externo.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
    }


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
