from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

ESCALA_CHOICES = [(i, str(i)) for i in range(1, 6)]


class RegistroHumorForm(FlaskForm):
    data = DateField("Data", validators=[DataRequired()])

    humor = SelectField("Humor (1 = péssimo, 5 = ótimo)", choices=ESCALA_CHOICES, coerce=int, validators=[DataRequired()])
    energia = SelectField("Energia (1 = exausto, 5 = cheio de energia)", choices=ESCALA_CHOICES, coerce=int, validators=[DataRequired()])
    motivacao = SelectField("Motivação (1 = nenhuma, 5 = muito motivado)", choices=ESCALA_CHOICES, coerce=int, validators=[DataRequired()])
    ansiedade = SelectField("Ansiedade (1 = tranquilo, 5 = muito ansioso)", choices=ESCALA_CHOICES, coerce=int, validators=[DataRequired()])
    estresse = SelectField("Estresse (1 = relaxado, 5 = muito estressado)", choices=ESCALA_CHOICES, coerce=int, validators=[DataRequired()])

    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Salvar registro")
