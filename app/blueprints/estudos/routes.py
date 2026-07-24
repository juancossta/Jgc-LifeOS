from datetime import date, timedelta
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.estudos import RegistroEstudo
from app.models.projetos import Projeto
from app.blueprints.estudos.forms import RegistroEstudoForm

estudos_bp = Blueprint("estudos", __name__, template_folder="../../templates/estudos")


def _popular_projetos(form):
    projetos = Projeto.query.filter_by(user_id=current_user.id).order_by(Projeto.nome).all()
    form.projeto_id.choices = [(0, "Nenhum")] + [(p.id, p.nome) for p in projetos]


@estudos_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = (
        RegistroEstudo.query.filter_by(user_id=current_user.id)
        .order_by(RegistroEstudo.data.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )

    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    inicio_ano = hoje.replace(month=1, day=1)

    todos = RegistroEstudo.query.filter_by(user_id=current_user.id).all()

    horas_por_tecnologia = {}
    for r in todos:
        horas_por_tecnologia[r.tecnologia] = horas_por_tecnologia.get(r.tecnologia, 0) + r.horas
    top_tecnologias = sorted(horas_por_tecnologia.items(), key=lambda x: x[1], reverse=True)[:6]

    projetos_ativos = Projeto.query.filter_by(user_id=current_user.id, status="em_andamento").count()

    stats = {
        "horas_semana": sum(r.horas for r in todos if r.data >= inicio_semana),
        "horas_mes": sum(r.horas for r in todos if r.data >= inicio_mes),
        "horas_ano": sum(r.horas for r in todos if r.data >= inicio_ano),
        "total_registros": len(todos),
        "projetos_ativos": projetos_ativos,
    }

    return render_template(
        "estudos/index.html",
        pagination=pagination,
        stats=stats,
        top_tecnologias=top_tecnologias,
    )


@estudos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = RegistroEstudoForm(obj=SimpleNamespace(data=date.today(), projeto_id=0))
    _popular_projetos(form)

    if form.validate_on_submit():
        registro = RegistroEstudo(
            user_id=current_user.id,
            data=form.data.data,
            tecnologia=form.tecnologia.data.strip(),
            horas=form.horas.data,
            projeto_id=form.projeto_id.data or None,
            curso=form.curso.data,
            descricao=form.descricao.data,
            observacoes=form.observacoes.data,
        )
        db.session.add(registro)
        db.session.commit()
        flash("Registro de estudo salvo com sucesso.", "success")
        return redirect(url_for("estudos.index"))

    return render_template("estudos/form.html", form=form, titulo="Novo registro")


@estudos_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(registro_id):
    registro = RegistroEstudo.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    form = RegistroEstudoForm(obj=registro)
    form.projeto_id.data = registro.projeto_id or 0
    _popular_projetos(form)

    if form.validate_on_submit():
        registro.data = form.data.data
        registro.tecnologia = form.tecnologia.data.strip()
        registro.horas = form.horas.data
        registro.projeto_id = form.projeto_id.data or None
        registro.curso = form.curso.data
        registro.descricao = form.descricao.data
        registro.observacoes = form.observacoes.data
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("estudos.index"))

    return render_template("estudos/form.html", form=form, titulo="Editar registro")


@estudos_bp.route("/<int:registro_id>/excluir", methods=["POST"])
@login_required
def excluir(registro_id):
    registro = RegistroEstudo.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash("Registro excluído.", "info")
    return redirect(url_for("estudos.index"))
