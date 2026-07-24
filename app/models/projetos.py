from datetime import datetime, date
from app.extensions import db

STATUS_CHOICES = [
    ("planejado", "Planejado"),
    ("em_andamento", "Em andamento"),
    ("pausado", "Pausado"),
    ("concluido", "Concluído"),
    ("cancelado", "Cancelado"),
]

PRIORIDADE_CHOICES = [
    ("baixa", "Baixa"),
    ("media", "Média"),
    ("alta", "Alta"),
    ("urgente", "Urgente"),
]


class Projeto(db.Model):
    __tablename__ = "projetos"
    __table_args__ = (
        db.Index("ix_projetos_user_status", "user_id", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="planejado")
    prioridade = db.Column(db.String(20), nullable=False, default="media")

    data_inicio = db.Column(db.Date, default=date.today)
    prazo = db.Column(db.Date)

    horas_investidas = db.Column(db.Float, default=0)
    percentual_concluido = db.Column(db.Integer, default=0)  # usado quando não há checklist
    anotacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    checklist = db.relationship(
        "ChecklistItem",
        backref="projeto",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ChecklistItem.criado_em",
    )

    @property
    def status_label(self):
        return dict(STATUS_CHOICES).get(self.status, self.status)

    @property
    def prioridade_label(self):
        return dict(PRIORIDADE_CHOICES).get(self.prioridade, self.prioridade)

    @property
    def progresso(self):
        """Se houver itens no checklist, o progresso é calculado automaticamente por eles.
        Caso contrário, usa o percentual manual informado no projeto."""
        total = self.checklist.count()
        if total == 0:
            return self.percentual_concluido or 0
        concluidos = self.checklist.filter_by(concluido=True).count()
        return round((concluidos / total) * 100)

    @property
    def atrasado(self):
        return bool(self.prazo and self.prazo < date.today() and self.status not in ("concluido", "cancelado"))

    def __repr__(self):
        return f"<Projeto {self.nome}>"


class ChecklistItem(db.Model):
    __tablename__ = "checklist_items"

    id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey("projetos.id", ondelete="CASCADE"), nullable=False)

    texto = db.Column(db.String(255), nullable=False)
    concluido = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChecklistItem {self.texto}>"
