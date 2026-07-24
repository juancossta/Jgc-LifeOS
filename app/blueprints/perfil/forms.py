from flask_wtf import FlaskForm
from wtforms import (
    FloatField, IntegerField, StringField, TimeField, BooleanField, SubmitField
)
from wtforms.validators import Optional, NumberRange, Length, DataRequired


class PerfilForm(FlaskForm):
    altura_cm = FloatField("Altura (cm)", validators=[Optional(), NumberRange(min=50, max=250)])
    meta_agua_ml = IntegerField("Meta diária de água (ml)", validators=[Optional(), NumberRange(min=0)], default=2000)
    meta_sono_horas = FloatField("Meta diária de sono (horas)", validators=[Optional(), NumberRange(min=0, max=24)], default=7)
    telegram_chat_id = StringField("Chat ID do Telegram", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Salvar preferências")


class LembreteForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(min=2, max=100)])
    mensagem = StringField("Mensagem (opcional, padrão usa o título)", validators=[Optional(), Length(max=255)])
    hora = TimeField("Horário", validators=[DataRequired()])

    seg = BooleanField("Seg", default=True)
    ter = BooleanField("Ter", default=True)
    qua = BooleanField("Qua", default=True)
    qui = BooleanField("Qui", default=True)
    sex = BooleanField("Sex", default=True)
    sab = BooleanField("Sáb", default=False)
    dom = BooleanField("Dom", default=False)

    ativo = BooleanField("Ativo", default=True)
    submit = SubmitField("Salvar lembrete")
