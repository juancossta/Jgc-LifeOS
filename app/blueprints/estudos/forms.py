from flask_wtf import FlaskForm
from wtforms import (
    StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class RegistroEstudoForm(FlaskForm):
    data = DateField("Data", validators=[DataRequired()])
    tecnologia = StringField("Tecnologia", validators=[DataRequired(), Length(min=2, max=80)])
    horas = FloatField("Horas estudadas", validators=[DataRequired(), NumberRange(min=0.1, max=24)])
    projeto_id = SelectField("Projeto vinculado", coerce=int, validators=[Optional()])
    curso = StringField("Curso", validators=[Optional(), Length(max=150)])
    descricao = TextAreaField("Descrição", validators=[Optional()])
    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Salvar registro")
