from datetime import date, timedelta
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.pureza import RegistroPureza
from app.blueprints.pureza.forms import RegistroPurezaForm

pureza_bp = Blueprint("pureza", __name__, template_folder="../../templates/pureza")


def _dias_consecutivos_resistindo(user_id):
    """Conta a sequência atual de dias consecutivos (a partir de hoje) em que houve
    registro e o usuário resistiu. Um dia sem registro ou uma recaída interrompe a sequência."""
    registros = {
        r.data: r.resistiu
        for r in RegistroPureza.query.filter_by(user_id=user_id).all()
    }
    dias = 0
    cursor = date.today()
    while cursor in registros and registros[cursor]:
        dias += 1
        cursor -= timedelta(days=1)
    return dias


@pureza_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = (
        RegistroPureza.query.filter_by(user_id=current_user.id)
        .order_by(RegistroPureza.data.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )

    todos = RegistroPureza.query.filter_by(user_id=current_user.id).all()
    total = len(todos)
    resistiu_count = sum(1 for r in todos if r.resistiu)

    stats = {
        "dias_consecutivos": _dias_consecutivos_resistindo(current_user.id),
        "total_registros": total,
        "taxa_sucesso": round((resistiu_count / total) * 100) if total else 0,
    }

    return render_template("pureza/index.html", pagination=pagination, stats=stats)


@pureza_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = RegistroPurezaForm(obj=SimpleNamespace(data=date.today(), resistiu=True))
    if form.validate_on_submit():
        existente = RegistroPureza.query.filter_by(user_id=current_user.id, data=form.data.data).first()
        if existente:
            flash("Você já tem um registro de pureza nesse dia. Edite o registro existente.", "danger")
            return render_template("pureza/form.html", form=form, titulo="Novo registro")

        registro = RegistroPureza(user_id=current_user.id, data=form.data.data, resistiu=form.resistiu.data)
        _aplicar_campos_condicionais(registro, form)
        db.session.add(registro)
        db.session.commit()
        flash("Registro salvo com sucesso.", "success")
        return redirect(url_for("pureza.index"))

    return render_template("pureza/form.html", form=form, titulo="Novo registro")


@pureza_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(registro_id):
    registro = RegistroPureza.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    form = RegistroPurezaForm(obj=registro)

    if form.validate_on_submit():
        registro.data = form.data.data
        registro.resistiu = form.resistiu.data
        _aplicar_campos_condicionais(registro, form)
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("pureza.index"))

    return render_template("pureza/form.html", form=form, titulo="Editar registro")


@pureza_bp.route("/<int:registro_id>/excluir", methods=["POST"])
@login_required
def excluir(registro_id):
    registro = RegistroPureza.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash("Registro excluído.", "info")
    return redirect(url_for("pureza.index"))


def _aplicar_campos_condicionais(registro, form):
    """Quando resistiu=True, os campos condicionais são limpos (escondidos/zerados),
    conforme especificado: 'Esconder novamente ao selecionar Sim'."""
    if form.resistiu.data:
        registro.gatilho = None
        registro.local = None
        registro.sentimento = None
        registro.como_evitar = None
        registro.orou_depois = False
        registro.versiculo = None
    else:
        registro.gatilho = form.gatilho.data
        registro.local = form.local.data
        registro.sentimento = form.sentimento.data
        registro.como_evitar = form.como_evitar.data
        registro.orou_depois = form.orou_depois.data
        registro.versiculo = form.versiculo.data
    registro.observacoes = form.observacoes.data
