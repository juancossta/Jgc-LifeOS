from datetime import datetime, date
from app.extensions import db


class RegistroFe(db.Model):
    __tablename__ = "registros_fe"
    __table_args__ = (
        db.Index("ix_fe_user_data", "user_id", "data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    data = db.Column(db.Date, nullable=False, default=date.today)

    livro = db.Column(db.String(60))
    capitulo_inicial = db.Column(db.Integer)
    capitulo_final = db.Column(db.Integer)
    tempo_leitura_min = db.Column(db.Integer, default=0)

    orou = db.Column(db.Boolean, default=False)
    tempo_oracao_min = db.Column(db.Integer, default=0)

    devocional = db.Column(db.Text)
    versiculo_favorito = db.Column(db.String(255))
    aprendizado = db.Column(db.Text)
    observacoes = db.Column(db.Text)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def qtd_capitulos(self):
        if self.capitulo_inicial is None or self.capitulo_final is None:
            return 0
        return max(0, self.capitulo_final - self.capitulo_inicial + 1)

    def __repr__(self):
        return f"<RegistroFe {self.data} {self.livro}>"
