from flask_wtf import FlaskForm
from wtforms import (
    StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models.financeiro import TIPO_TRANSACAO_CHOICES, TIPO_INVESTIMENTO_CHOICES


class TransacaoForm(FlaskForm):
    tipo = SelectField("Tipo", choices=TIPO_TRANSACAO_CHOICES, validators=[DataRequired()])
    valor = FloatField("Valor", validators=[DataRequired(), NumberRange(min=0.01)])
    data = DateField("Data", validators=[DataRequired()])
    categoria_id = SelectField("Categoria", coerce=int, validators=[Optional()])
    descricao = StringField("Descrição", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Salvar transação")


class CategoriaFinanceiraForm(FlaskForm):
    nome = StringField("Nome da categoria", validators=[DataRequired(), Length(min=2, max=60)])
    tipo = SelectField("Tipo", choices=TIPO_TRANSACAO_CHOICES, validators=[DataRequired()])
    submit = SubmitField("Adicionar categoria")


class ObjetivoFinanceiroForm(FlaskForm):
    titulo = StringField("Título do objetivo", validators=[DataRequired(), Length(min=2, max=150)])
    valor_atual = FloatField("Valor atual", validators=[Optional(), NumberRange(min=0)], default=0)
    valor_meta = FloatField("Valor da meta", validators=[DataRequired(), NumberRange(min=0.01)])
    prazo = DateField("Prazo", validators=[Optional()])
    submit = SubmitField("Salvar objetivo")


class InvestimentoForm(FlaskForm):
    nome = StringField("Nome do investimento", validators=[DataRequired(), Length(min=2, max=150)])
    tipo = SelectField("Tipo", choices=TIPO_INVESTIMENTO_CHOICES, validators=[DataRequired()])
    valor_investido = FloatField("Valor investido", validators=[DataRequired(), NumberRange(min=0)])
    valor_atual = FloatField("Valor atual", validators=[DataRequired(), NumberRange(min=0)])
    data_aplicacao = DateField("Data da aplicação", validators=[Optional()])
    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Salvar investimento")
