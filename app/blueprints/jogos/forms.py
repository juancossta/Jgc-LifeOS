from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class RegistroJogoForm(FlaskForm):
    data = DateField("Data", validators=[DataRequired()])
    jogo = StringField("Jogo", validators=[DataRequired(), Length(min=1, max=120)])
    tempo_minutos = IntegerField("Tempo jogado (min)", validators=[DataRequired(), NumberRange(min=1, max=1440)])
    plataforma = StringField("Plataforma", validators=[Optional(), Length(max=60)])
    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Salvar registro")
