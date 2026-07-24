from datetime import datetime, date
from app.extensions import db


class RegistroJogo(db.Model):
    __tablename__ = "registros_jogo"
    __table_args__ = (
        db.Index("ix_jogo_user_data", "user_id", "data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    data = db.Column(db.Date, nullable=False, default=date.today)
    jogo = db.Column(db.String(120), nullable=False)
    tempo_minutos = db.Column(db.Integer, nullable=False, default=0)
    plataforma = db.Column(db.String(60))
    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RegistroJogo {self.data} {self.jogo}>"
