from flask_wtf import FlaskForm
from wtforms import (
    DateField, FloatField, IntegerField, BooleanField, StringField, TextAreaField, SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class RegistroSaudeForm(FlaskForm):
    data = DateField("Data", validators=[DataRequired()])

    peso = FloatField("Peso (kg)", validators=[Optional(), NumberRange(min=1, max=400)])
    agua_ml = IntegerField("Água (ml)", validators=[Optional(), NumberRange(min=0)], default=0)
    sono_horas = FloatField("Sono (horas)", validators=[Optional(), NumberRange(min=0, max=24)], default=0)

    treinou = BooleanField("Treinou hoje")
    tipo_treino = StringField("Tipo de treino", validators=[Optional(), Length(max=80)])
    cardio_min = IntegerField("Cardio (min)", validators=[Optional(), NumberRange(min=0)], default=0)
    passos = IntegerField("Passos", validators=[Optional(), NumberRange(min=0)], default=0)

    observacoes = TextAreaField("Observações", validators=[Optional()])

    submit = SubmitField("Salvar registro")
