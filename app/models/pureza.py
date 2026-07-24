from datetime import datetime, date
from app.extensions import db


class RegistroPureza(db.Model):
    __tablename__ = "registros_pureza"
    __table_args__ = (
        db.Index("ix_pureza_user_data", "user_id", "data"),
        db.UniqueConstraint("user_id", "data", name="uq_pureza_user_data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    data = db.Column(db.Date, nullable=False, default=date.today)
    resistiu = db.Column(db.Boolean, nullable=False, default=True)

    # Campos condicionais — só relevantes quando resistiu=False
    gatilho = db.Column(db.String(255))
    local = db.Column(db.String(150))
    sentimento = db.Column(db.String(150))
    como_evitar = db.Column(db.Text)
    orou_depois = db.Column(db.Boolean, default=False)
    versiculo = db.Column(db.String(255))

    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RegistroPureza {self.data} resistiu={self.resistiu}>"
