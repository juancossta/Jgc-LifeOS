from datetime import time
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.lembretes import Lembrete, DIAS_SEMANA
from app.blueprints.perfil.forms import PerfilForm, LembreteForm
from app.utils.telegram import enviar_telegram

perfil_bp = Blueprint("perfil", __name__, template_folder="../../templates/perfil")

DIAS_CAMPOS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


@perfil_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = PerfilForm(obj=current_user)
    if form.validate_on_submit():
        current_user.altura_cm = form.altura_cm.data
        current_user.meta_agua_ml = form.meta_agua_ml.data or 2000
        current_user.meta_sono_horas = form.meta_sono_horas.data or 7
        current_user.telegram_chat_id = form.telegram_chat_id.data
        db.session.commit()
        flash("Preferências salvas.", "success")
        return redirect(url_for("perfil.index"))

    lembretes = Lembrete.query.filter_by(user_id=current_user.id).order_by(Lembrete.hora).all()
    return render_template("perfil/index.html", form=form, lembretes=lembretes)


@perfil_bp.route("/testar-telegram", methods=["POST"])
@login_required
def testar_telegram():
    ok, detalhe = enviar_telegram(
        current_user.telegram_chat_id,
        "🔔 LifeOS: notificação de teste. Se você recebeu isso, seus lembretes vão funcionar!",
    )
    flash(detalhe, "success" if ok else "danger")
    return redirect(url_for("perfil.index"))


@perfil_bp.route("/lembretes/novo", methods=["GET", "POST"])
@login_required
def lembrete_novo():
    form = LembreteForm(hora=time(19, 0))
    if form.validate_on_submit():
        dias = _dias_selecionados(form)
        if not dias:
            flash("Selecione ao menos um dia da semana.", "danger")
        else:
            lembrete = Lembrete(
                user_id=current_user.id,
                titulo=form.titulo.data,
                mensagem=form.mensagem.data,
                hora=form.hora.data,
                dias_semana=",".join(dias),
                ativo=form.ativo.data,
            )
            db.session.add(lembrete)
            db.session.commit()
            flash("Lembrete criado.", "success")
            return redirect(url_for("perfil.index"))

    return render_template("perfil/lembrete_form.html", form=form, titulo="Novo lembrete")


@perfil_bp.route("/lembretes/<int:lembrete_id>/editar", methods=["GET", "POST"])
@login_required
def lembrete_editar(lembrete_id):
    lembrete = Lembrete.query.filter_by(id=lembrete_id, user_id=current_user.id).first_or_404()

    if request.method == "GET":
        form = LembreteForm(obj=lembrete)
        dias_ativos = lembrete.dias_semana_lista
        for i, campo in enumerate(DIAS_CAMPOS):
            getattr(form, campo).data = i in dias_ativos
    else:
        form = LembreteForm()

    if form.validate_on_submit():
        dias = _dias_selecionados(form)
        if not dias:
            flash("Selecione ao menos um dia da semana.", "danger")
        else:
            lembrete.titulo = form.titulo.data
            lembrete.mensagem = form.mensagem.data
            lembrete.hora = form.hora.data
            lembrete.dias_semana = ",".join(dias)
            lembrete.ativo = form.ativo.data
            db.session.commit()
            flash("Lembrete atualizado.", "success")
            return redirect(url_for("perfil.index"))

    return render_template("perfil/lembrete_form.html", form=form, titulo="Editar lembrete")


@perfil_bp.route("/lembretes/<int:lembrete_id>/excluir", methods=["POST"])
@login_required
def lembrete_excluir(lembrete_id):
    lembrete = Lembrete.query.filter_by(id=lembrete_id, user_id=current_user.id).first_or_404()
    db.session.delete(lembrete)
    db.session.commit()
    flash("Lembrete excluído.", "info")
    return redirect(url_for("perfil.index"))


def _dias_selecionados(form):
    dias = []
    for i, campo in enumerate(DIAS_CAMPOS):
        if getattr(form, campo).data:
            dias.append(str(i))
    return dias
