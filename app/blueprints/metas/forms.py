from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models.metas import CATEGORIA_META_CHOICES, STATUS_META_CHOICES


class MetaForm(FlaskForm):
    titulo = StringField("Título da meta", validators=[DataRequired(), Length(min=2, max=150)])
    categoria = SelectField("Categoria", choices=CATEGORIA_META_CHOICES, validators=[DataRequired()])
    objetivo = TextAreaField("Objetivo", validators=[Optional()])

    valor_atual = FloatField("Valor atual", validators=[Optional(), NumberRange(min=0)], default=0)
    valor_final = FloatField("Valor final (meta)", validators=[DataRequired(), NumberRange(min=0.01)])
    prazo = DateField("Prazo", validators=[Optional()])

    status = SelectField("Status", choices=STATUS_META_CHOICES, validators=[DataRequired()])

    submit = SubmitField("Salvar meta")
