from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, BooleanField, TextAreaField, DateField, SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange


class RegistroFeForm(FlaskForm):
    data = DateField("Data", validators=[DataRequired()])

    livro = StringField("Livro", validators=[Optional()])
    capitulo_inicial = IntegerField("Capítulo inicial", validators=[Optional(), NumberRange(min=1)])
    capitulo_final = IntegerField("Capítulo final", validators=[Optional(), NumberRange(min=1)])
    tempo_leitura_min = IntegerField("Tempo de leitura (min)", validators=[Optional(), NumberRange(min=0)], default=0)

    orou = BooleanField("Orou hoje")
    tempo_oracao_min = IntegerField("Tempo de oração (min)", validators=[Optional(), NumberRange(min=0)], default=0)

    devocional = TextAreaField("Devocional", validators=[Optional()])
    versiculo_favorito = StringField("Versículo favorito", validators=[Optional()])
    aprendizado = TextAreaField("Aprendizado", validators=[Optional()])
    observacoes = TextAreaField("Observações", validators=[Optional()])

    submit = SubmitField("Salvar registro")

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators)
        if self.capitulo_inicial.data and self.capitulo_final.data:
            if self.capitulo_final.data < self.capitulo_inicial.data:
                self.capitulo_final.errors.append(
                    "O capítulo final não pode ser menor que o inicial."
                )
                ok = False
        return ok
