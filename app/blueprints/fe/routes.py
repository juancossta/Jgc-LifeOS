from datetime import date, timedelta
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.fe import RegistroFe
from app.blueprints.fe.forms import RegistroFeForm

fe_bp = Blueprint("fe", __name__, template_folder="../../templates/fe")


@fe_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = (
        RegistroFe.query.filter_by(user_id=current_user.id)
        .order_by(RegistroFe.data.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )

    todos = RegistroFe.query.filter_by(user_id=current_user.id).all()
    stats = {
        "total_capitulos": sum(r.qtd_capitulos for r in todos),
        "total_tempo_leitura": sum(r.tempo_leitura_min or 0 for r in todos),
        "total_tempo_oracao": sum(r.tempo_oracao_min or 0 for r in todos),
        "total_registros": len(todos),
    }

    return render_template("fe/index.html", pagination=pagination, stats=stats)


@fe_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = RegistroFeForm(obj=SimpleNamespace(data=date.today()))
    if form.validate_on_submit():
        registro = RegistroFe(
            user_id=current_user.id,
            data=form.data.data,
            livro=form.livro.data,
            capitulo_inicial=form.capitulo_inicial.data,
            capitulo_final=form.capitulo_final.data,
            tempo_leitura_min=form.tempo_leitura_min.data or 0,
            orou=form.orou.data,
            tempo_oracao_min=form.tempo_oracao_min.data or 0,
            devocional=form.devocional.data,
            versiculo_favorito=form.versiculo_favorito.data,
            aprendizado=form.aprendizado.data,
            observacoes=form.observacoes.data,
        )
        db.session.add(registro)
        db.session.commit()
        flash("Registro de fé salvo com sucesso.", "success")
        return redirect(url_for("fe.index"))

    return render_template("fe/form.html", form=form, titulo="Novo registro")


@fe_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(registro_id):
    registro = RegistroFe.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    form = RegistroFeForm(obj=registro)

    if form.validate_on_submit():
        form.populate_obj(registro)
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("fe.index"))

    return render_template("fe/form.html", form=form, titulo="Editar registro")


@fe_bp.route("/<int:registro_id>/excluir", methods=["POST"])
@login_required
def excluir(registro_id):
    registro = RegistroFe.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash("Registro excluído.", "info")
    return redirect(url_for("fe.index"))
