from datetime import datetime, date
from app.extensions import db


class RegistroEstudo(db.Model):
    __tablename__ = "registros_estudo"
    __table_args__ = (
        db.Index("ix_estudo_user_data", "user_id", "data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey("projetos.id", ondelete="SET NULL"), nullable=True)

    data = db.Column(db.Date, nullable=False, default=date.today)
    tecnologia = db.Column(db.String(80), nullable=False)
    horas = db.Column(db.Float, nullable=False, default=0)
    curso = db.Column(db.String(150))
    descricao = db.Column(db.Text)
    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    projeto = db.relationship("Projeto", backref=db.backref("registros_estudo", lazy="dynamic"))

    def __repr__(self):
        return f"<RegistroEstudo {self.data} {self.tecnologia}>"
