from datetime import datetime, date
from app.extensions import db


class RegistroSaude(db.Model):
    __tablename__ = "registros_saude"
    __table_args__ = (
        db.Index("ix_saude_user_data", "user_id", "data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    data = db.Column(db.Date, nullable=False, default=date.today)

    peso = db.Column(db.Float)  # kg
    agua_ml = db.Column(db.Integer, default=0)
    sono_horas = db.Column(db.Float, default=0)

    treinou = db.Column(db.Boolean, default=False)
    tipo_treino = db.Column(db.String(80))
    cardio_min = db.Column(db.Integer, default=0)
    passos = db.Column(db.Integer, default=0)

    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RegistroSaude {self.data}>"
