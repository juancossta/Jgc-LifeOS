from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Perfil / preferências de saúde
    altura_cm = db.Column(db.Float)
    meta_agua_ml = db.Column(db.Integer, default=2000)
    meta_sono_horas = db.Column(db.Float, default=7)

    # Notificações (Telegram)
    telegram_chat_id = db.Column(db.String(50))

    # Redefinição de senha
    reset_token = db.Column(db.String(100))
    reset_token_expira = db.Column(db.DateTime)

    registros_fe = db.relationship(
        "RegistroFe", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    projetos = db.relationship(
        "Projeto", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    transacoes = db.relationship(
        "Transacao", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    categorias_financeiras = db.relationship(
        "CategoriaFinanceira", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    objetivos_financeiros = db.relationship(
        "ObjetivoFinanceiro", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    investimentos = db.relationship(
        "Investimento", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    registros_estudo = db.relationship(
        "RegistroEstudo", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    metas = db.relationship(
        "Meta", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    registros_saude = db.relationship(
        "RegistroSaude", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    registros_humor = db.relationship(
        "RegistroHumor", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    registros_pureza = db.relationship(
        "RegistroPureza", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    registros_jogo = db.relationship(
        "RegistroJogo", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    lembretes = db.relationship(
        "Lembrete", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def calcular_imc(self, peso_kg):
        if not self.altura_cm or not peso_kg:
            return None
        altura_m = self.altura_cm / 100
        return round(peso_kg / (altura_m ** 2), 1)

    @staticmethod
    def classificar_imc(imc):
        if imc is None:
            return None
        if imc < 18.5:
            return "Abaixo do peso"
        if imc < 25:
            return "Peso normal"
        if imc < 30:
            return "Sobrepeso"
        return "Obesidade"

    def gerar_token_redefinicao(self):
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expira = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def token_redefinicao_valido(self, token):
        if not self.reset_token or not self.reset_token_expira:
            return False
        if self.reset_token != token:
            return False
        return datetime.utcnow() <= self.reset_token_expira

    def limpar_token_redefinicao(self):
        self.reset_token = None
        self.reset_token_expira = None

    def __repr__(self):
        return f"<User {self.email}>"