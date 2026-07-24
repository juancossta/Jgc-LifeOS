from flask_wtf import FlaskForm
from wtforms import DateField, BooleanField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class RegistroPurezaForm(FlaskForm):
    data = DateField("Data", validators=[DataRequired()])
    resistiu = BooleanField("Resistiu às tentações hoje?", default=True)

    # Campos condicionais (exibidos apenas quando resistiu = Não)
    gatilho = StringField("Gatilho", validators=[Optional(), Length(max=255)])
    local = StringField("Local", validators=[Optional(), Length(max=150)])
    sentimento = StringField("Sentimento", validators=[Optional(), Length(max=150)])
    como_evitar = TextAreaField("Como evitar da próxima vez", validators=[Optional()])
    orou_depois = BooleanField("Orou depois?")
    versiculo = StringField("Versículo", validators=[Optional(), Length(max=255)])

    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Salvar registro")

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators)
        return ok
