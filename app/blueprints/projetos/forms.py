from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, DateField, FloatField,
    IntegerField, SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models.projetos import STATUS_CHOICES, PRIORIDADE_CHOICES


class ProjetoForm(FlaskForm):
    nome = StringField("Nome do projeto", validators=[DataRequired(), Length(min=2, max=150)])
    descricao = TextAreaField("Descrição", validators=[Optional()])
    status = SelectField("Status", choices=STATUS_CHOICES, validators=[DataRequired()])
    prioridade = SelectField("Prioridade", choices=PRIORIDADE_CHOICES, validators=[DataRequired()])

    data_inicio = DateField("Data de início", validators=[Optional()])
    prazo = DateField("Prazo", validators=[Optional()])

    horas_investidas = FloatField("Horas investidas", validators=[Optional(), NumberRange(min=0)], default=0)
    percentual_concluido = IntegerField(
        "% concluído (usado se não houver checklist)",
        validators=[Optional(), NumberRange(min=0, max=100)], default=0
    )
    anotacoes = TextAreaField("Anotações", validators=[Optional()])

    submit = SubmitField("Salvar projeto")

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators)
        if self.data_inicio.data and self.prazo.data and self.prazo.data < self.data_inicio.data:
            self.prazo.errors.append("O prazo não pode ser anterior à data de início.")
            ok = False
        return ok


class ChecklistItemForm(FlaskForm):
    texto = StringField("Item do checklist", validators=[DataRequired(), Length(min=1, max=255)])
    submit = SubmitField("Adicionar")
