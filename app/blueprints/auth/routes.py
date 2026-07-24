from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.blueprints.auth.forms import LoginForm, RegisterForm

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
