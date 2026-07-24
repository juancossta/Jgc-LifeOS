from datetime import datetime, date
from app.extensions import db

CATEGORIA_META_CHOICES = [
    ("fe", "Fé"),
    ("saude", "Saúde"),
    ("estudos", "Estudos"),
    ("projetos", "Projetos"),
    ("financeiro", "Financeiro"),
    ("pessoal", "Pessoal"),
    ("outro", "Outro"),
]

STATUS_META_CHOICES = [
    ("em_andamento", "Em andamento"),
    ("concluida", "Concluída"),
    ("cancelada", "Cancelada"),
]


class Meta(db.Model):
    __tablename__ = "metas"
    __table_args__ = (
        db.Index("ix_metas_user_status", "user_id", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    titulo = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(20), nullable=False, default="pessoal")
    objetivo = db.Column(db.Text)

    valor_atual = db.Column(db.Float, default=0)
    valor_final = db.Column(db.Float, nullable=False, default=100)
    prazo = db.Column(db.Date)

    status = db.Column(db.String(20), nullable=False, default="em_andamento")

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def categoria_label(self):
        return dict(CATEGORIA_META_CHOICES).get(self.categoria, self.categoria)

    @property
    def status_label(self):
        return dict(STATUS_META_CHOICES).get(self.status, self.status)

    @property
    def progresso(self):
        if not self.valor_final:
            return 0
        return max(0, min(100, round((self.valor_atual / self.valor_final) * 100)))

    @property
    def atrasada(self):
        return bool(
            self.prazo and self.prazo < date.today() and self.status == "em_andamento"
        )

    def __repr__(self):
        return f"<Meta {self.titulo}>"
