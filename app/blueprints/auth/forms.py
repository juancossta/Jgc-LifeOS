from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    lembrar = BooleanField("Lembrar de mim")
    submit = SubmitField("Entrar")


class RegisterForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField(
        "Confirmar senha",
        validators=[DataRequired(), EqualTo("senha", message="As senhas não coincidem.")],
    )
    submit = SubmitField("Criar conta")


class EsqueciSenhaForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    submit = SubmitField("Enviar link de redefinição")


class RedefinirSenhaForm(FlaskForm):
    senha = PasswordField("Nova senha", validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField(
        "Confirmar nova senha",
        validators=[DataRequired(), EqualTo("senha", message="As senhas não coincidem.")],
    )
    submit = SubmitField("Redefinir senha")