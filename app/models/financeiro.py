from datetime import datetime, date
from app.extensions import db

TIPO_TRANSACAO_CHOICES = [
    ("receita", "Receita"),
    ("despesa", "Despesa"),
]

TIPO_INVESTIMENTO_CHOICES = [
    ("renda_fixa", "Renda Fixa"),
    ("renda_variavel", "Renda Variável"),
    ("cripto", "Criptomoeda"),
    ("outro", "Outro"),
]


class CategoriaFinanceira(db.Model):
    __tablename__ = "categorias_financeiras"
    __table_args__ = (
        db.UniqueConstraint("user_id", "nome", "tipo", name="uq_categoria_user_nome_tipo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    nome = db.Column(db.String(60), nullable=False)
    tipo = db.Column(db.String(10), nullable=False, default="despesa")  # receita | despesa

    transacoes = db.relationship("Transacao", backref="categoria", lazy="dynamic")

    def __repr__(self):
        return f"<CategoriaFinanceira {self.nome}>"


class Transacao(db.Model):
    __tablename__ = "transacoes"
    __table_args__ = (
        db.Index("ix_transacoes_user_data", "user_id", "data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_financeiras.id", ondelete="SET NULL"), nullable=True)

    tipo = db.Column(db.String(10), nullable=False)  # receita | despesa
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    descricao = db.Column(db.String(255))

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def valor_assinado(self):
        return self.valor if self.tipo == "receita" else -self.valor

    def __repr__(self):
        return f"<Transacao {self.tipo} {self.valor}>"


class ObjetivoFinanceiro(db.Model):
    __tablename__ = "objetivos_financeiros"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    titulo = db.Column(db.String(150), nullable=False)
    valor_atual = db.Column(db.Float, default=0)
    valor_meta = db.Column(db.Float, nullable=False)
    prazo = db.Column(db.Date)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def progresso(self):
        if not self.valor_meta:
            return 0
        return min(100, round((self.valor_atual / self.valor_meta) * 100))

    @property
    def concluido(self):
        return self.valor_atual >= self.valor_meta

    def __repr__(self):
        return f"<ObjetivoFinanceiro {self.titulo}>"


class Investimento(db.Model):
    __tablename__ = "investimentos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default="renda_fixa")
    valor_investido = db.Column(db.Float, nullable=False, default=0)
    valor_atual = db.Column(db.Float, nullable=False, default=0)
    data_aplicacao = db.Column(db.Date, default=date.today)
    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def tipo_label(self):
        return dict(TIPO_INVESTIMENTO_CHOICES).get(self.tipo, self.tipo)

    @property
    def rendimento_pct(self):
        if not self.valor_investido:
            return 0
        return round(((self.valor_atual - self.valor_investido) / self.valor_investido) * 100, 2)

    def __repr__(self):
        return f"<Investimento {self.nome}>"
