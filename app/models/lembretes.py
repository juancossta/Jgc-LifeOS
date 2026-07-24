from datetime import datetime
from app.extensions import db

DIAS_SEMANA = [
    ("0", "Seg"), ("1", "Ter"), ("2", "Qua"), ("3", "Qui"),
    ("4", "Sex"), ("5", "Sáb"), ("6", "Dom"),
]


class Lembrete(db.Model):
    __tablename__ = "lembretes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.String(255))
    hora = db.Column(db.Time, nullable=False)

    # Dias da semana em que o lembrete é ativo, ex: "0,1,2,3,4" (seg a sex). 0=segunda ... 6=domingo
    dias_semana = db.Column(db.String(20), nullable=False, default="0,1,2,3,4,5,6")

    ativo = db.Column(db.Boolean, default=True)
    ultimo_disparo = db.Column(db.Date)  # evita reenviar no mesmo dia

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def dias_semana_lista(self):
        return [int(d) for d in self.dias_semana.split(",") if d != ""]

    @property
    def dias_semana_label(self):
        nomes = dict(DIAS_SEMANA)
        return ", ".join(nomes[d] for d in self.dias_semana.split(",") if d in nomes)

    def texto_notificacao(self):
        return self.mensagem or f"⏰ {self.titulo}"

    def __repr__(self):
        return f"<Lembrete {self.titulo} {self.hora}>"
