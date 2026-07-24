from datetime import date, timedelta
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.jogos import RegistroJogo
from app.blueprints.jogos.forms import RegistroJogoForm

jogos_bp = Blueprint("jogos", __name__, template_folder="../../templates/jogos")


@jogos_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = (
        RegistroJogo.query.filter_by(user_id=current_user.id)
        .order_by(RegistroJogo.data.desc(), RegistroJogo.criado_em.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )

    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())

    todos = RegistroJogo.query.filter_by(user_id=current_user.id).all()

    tempo_por_jogo = {}
    for r in todos:
        tempo_por_jogo[r.jogo] = tempo_por_jogo.get(r.jogo, 0) + r.tempo_minutos
    ranking = sorted(tempo_por_jogo.items(), key=lambda x: x[1], reverse=True)[:6]

    stats = {
        "tempo_hoje": sum(r.tempo_minutos for r in todos if r.data == hoje),
        "tempo_semana": sum(r.tempo_minutos for r in todos if r.data >= inicio_semana),
        "jogo_favorito": ranking[0][0] if ranking else "—",
        "total_registros": len(todos),
    }

    return render_template("jogos/index.html", pagination=pagination, stats=stats, ranking=ranking)


@jogos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = RegistroJogoForm(obj=SimpleNamespace(data=date.today()))
    if form.validate_on_submit():
        registro = RegistroJogo(
            user_id=current_user.id,
            data=form.data.data,
            jogo=form.jogo.data.strip(),
            tempo_minutos=form.tempo_minutos.data,
            plataforma=form.plataforma.data,
            observacoes=form.observacoes.data,
        )
        db.session.add(registro)
        db.session.commit()
        flash("Sessão de jogo registrada.", "success")
        return redirect(url_for("jogos.index"))

    return render_template("jogos/form.html", form=form, titulo="Novo registro")


@jogos_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(registro_id):
    registro = RegistroJogo.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    form = RegistroJogoForm(obj=registro)

    if form.validate_on_submit():
        registro.data = form.data.data
        registro.jogo = form.jogo.data.strip()
        registro.tempo_minutos = form.tempo_minutos.data
        registro.plataforma = form.plataforma.data
        registro.observacoes = form.observacoes.data
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("jogos.index"))

    return render_template("jogos/form.html", form=form, titulo="Editar registro")


@jogos_bp.route("/<int:registro_id>/excluir", methods=["POST"])
@login_required
def excluir(registro_id):
    registro = RegistroJogo.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash("Registro excluído.", "info")
    return redirect(url_for("jogos.index"))
