from datetime import datetime, date
from app.extensions import db


class RegistroHumor(db.Model):
    __tablename__ = "registros_humor"
    __table_args__ = (
        db.Index("ix_humor_user_data", "user_id", "data"),
        db.UniqueConstraint("user_id", "data", name="uq_humor_user_data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    data = db.Column(db.Date, nullable=False, default=date.today)

    # Escalas de 1 a 5
    humor = db.Column(db.Integer, nullable=False, default=3)
    energia = db.Column(db.Integer, nullable=False, default=3)
    motivacao = db.Column(db.Integer, nullable=False, default=3)
    ansiedade = db.Column(db.Integer, nullable=False, default=3)
    estresse = db.Column(db.Integer, nullable=False, default=3)

    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def media_bem_estar(self):
        """Média simples considerando humor/energia/motivação como positivos
        e ansiedade/estresse como negativos (invertidos numa escala de 1-5)."""
        positivos = (self.humor + self.energia + self.motivacao) / 3
        negativos_invertidos = ((6 - self.ansiedade) + (6 - self.estresse)) / 2
        return round((positivos + negativos_invertidos) / 2, 1)

    def __repr__(self):
        return f"<RegistroHumor {self.data}>"
