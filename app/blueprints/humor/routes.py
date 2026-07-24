from datetime import date
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.humor import RegistroHumor
from app.blueprints.humor.forms import RegistroHumorForm

humor_bp = Blueprint("humor", __name__, template_folder="../../templates/humor")


@humor_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = (
        RegistroHumor.query.filter_by(user_id=current_user.id)
        .order_by(RegistroHumor.data.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )

    todos = RegistroHumor.query.filter_by(user_id=current_user.id).order_by(RegistroHumor.data.asc()).all()

    stats = {
        "media_humor": round(sum(r.humor for r in todos) / len(todos), 1) if todos else 0,
        "media_energia": round(sum(r.energia for r in todos) / len(todos), 1) if todos else 0,
        "media_ansiedade": round(sum(r.ansiedade for r in todos) / len(todos), 1) if todos else 0,
        "media_estresse": round(sum(r.estresse for r in todos) / len(todos), 1) if todos else 0,
        "total_registros": len(todos),
    }

    ultimos = todos[-30:]
    labels = [r.data.strftime("%d/%m") for r in ultimos]
    serie_humor = [r.humor for r in ultimos]
    serie_energia = [r.energia for r in ultimos]
    serie_ansiedade = [r.ansiedade for r in ultimos]
    serie_estresse = [r.estresse for r in ultimos]

    return render_template(
        "humor/index.html",
        pagination=pagination,
        stats=stats,
        labels=labels,
        serie_humor=serie_humor,
        serie_energia=serie_energia,
        serie_ansiedade=serie_ansiedade,
        serie_estresse=serie_estresse,
    )


@humor_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = RegistroHumorForm(obj=SimpleNamespace(
        data=date.today(), humor=3, energia=3, motivacao=3, ansiedade=3, estresse=3
    ))
    if form.validate_on_submit():
        existente = RegistroHumor.query.filter_by(user_id=current_user.id, data=form.data.data).first()
        if existente:
            flash("Você já registrou seu humor nesse dia. Edite o registro existente.", "danger")
            return render_template("humor/form.html", form=form, titulo="Novo registro")

        registro = RegistroHumor(
            user_id=current_user.id,
            data=form.data.data,
            humor=form.humor.data,
            energia=form.energia.data,
            motivacao=form.motivacao.data,
            ansiedade=form.ansiedade.data,
            estresse=form.estresse.data,
            observacoes=form.observacoes.data,
        )
        db.session.add(registro)
        db.session.commit()
        flash("Registro de humor salvo com sucesso.", "success")
        return redirect(url_for("humor.index"))

    return render_template("humor/form.html", form=form, titulo="Novo registro")


@humor_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(registro_id):
    registro = RegistroHumor.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    form = RegistroHumorForm(obj=registro)

    if form.validate_on_submit():
        form.populate_obj(registro)
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("humor.index"))

    return render_template("humor/form.html", form=form, titulo="Editar registro")


@humor_bp.route("/<int:registro_id>/excluir", methods=["POST"])
@login_required
def excluir(registro_id):
    registro = RegistroHumor.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash("Registro excluído.", "info")
    return redirect(url_for("humor.index"))
