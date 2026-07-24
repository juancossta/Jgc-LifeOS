from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.blueprints.auth.forms import LoginForm, RegisterForm, EsqueciSenhaForm, RedefinirSenhaForm
from app.utils.telegram import enviar_telegram

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_senha(form.senha.data):
            login_user(user, remember=form.lembrar.data)
            next_page = request.args.get("next")
            flash(f"Bem-vindo de volta, {user.nome}!", "success")
            return redirect(next_page or url_for("dashboard.index"))
        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/registrar", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("Já existe uma conta com este e-mail.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(nome=form.nome.data.strip(), email=email)
        user.set_senha(form.senha.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Conta criada com sucesso! Bem-vindo ao LifeOS.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = EsqueciSenhaForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        # Mensagem genérica sempre igual, exista ou não o e-mail — evita que alguém
        # descubra quais e-mails têm conta só testando esse formulário.
        mensagem_generica = (
            "Se esse e-mail estiver cadastrado, um link de redefinição foi enviado pelo Telegram."
        )

        if user:
            token = user.gerar_token_redefinicao()
            db.session.commit()

            if user.telegram_chat_id:
                link = url_for("auth.redefinir_senha", token=token, _external=True)
                texto = (
                    f"🔑 Redefinição de senha do LifeOS solicitada.\n\n"
                    f"Se foi você, clique no link abaixo (válido por 1 hora):\n{link}\n\n"
                    f"Se não foi você, ignore esta mensagem."
                )
                enviar_telegram(user.telegram_chat_id, texto)
            else:
                # Sem Telegram configurado, não há como entregar o link.
                # Não expomos isso na mensagem genérica por segurança,
                # mas registramos para você mesmo perceber em uso solo.
                flash(
                    "Encontramos sua conta, mas ela não tem um Chat ID do Telegram salvo, "
                    "então não conseguimos enviar o link. Configure em /perfil primeiro "
                    "(ou peça a redefinição manual direto no banco).",
                    "danger",
                )
                return render_template("auth/esqueci_senha.html", form=form)

        flash(mensagem_generica, "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/esqueci_senha.html", form=form)


@auth_bp.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.token_redefinicao_valido(token):
        flash("Esse link é inválido ou expirou. Solicite um novo.", "danger")
        return redirect(url_for("auth.esqueci_senha"))

    form = RedefinirSenhaForm()
    if form.validate_on_submit():
        user.set_senha(form.senha.data)
        user.limpar_token_redefinicao()
        db.session.commit()
        flash("Senha redefinida com sucesso. Faça login com a nova senha.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/redefinir_senha.html", form=form, token=token)