from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.projetos import Projeto, ChecklistItem, STATUS_CHOICES
from app.blueprints.projetos.forms import ProjetoForm, ChecklistItemForm

projetos_bp = Blueprint("projetos", __name__, template_folder="../../templates/projetos")


@projetos_bp.route("/")
@login_required
def index():
    status_filtro = request.args.get("status", "")

    query = Projeto.query.filter_by(user_id=current_user.id)
    if status_filtro:
        query = query.filter_by(status=status_filtro)

    projetos = query.order_by(Projeto.prioridade.desc(), Projeto.criado_em.desc()).all()

    todos = Projeto.query.filter_by(user_id=current_user.id).all()
    stats = {
        "total": len(todos),
        "em_andamento": sum(1 for p in todos if p.status == "em_andamento"),
        "concluidos": sum(1 for p in todos if p.status == "concluido"),
        "atrasados": sum(1 for p in todos if p.atrasado),
        "horas_totais": sum(p.horas_investidas or 0 for p in todos),
    }

    return render_template(
        "projetos/index.html",
        projetos=projetos,
        stats=stats,
        status_choices=STATUS_CHOICES,
        status_filtro=status_filtro,
    )


@projetos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = ProjetoForm(status="planejado", prioridade="media", data_inicio=date.today())
    if form.validate_on_submit():
        projeto = Projeto(
            user_id=current_user.id,
            nome=form.nome.data,
            descricao=form.descricao.data,
            status=form.status.data,
            prioridade=form.prioridade.data,
            data_inicio=form.data_inicio.data,
            prazo=form.prazo.data,
            horas_investidas=form.horas_investidas.data or 0,
            percentual_concluido=form.percentual_concluido.data or 0,
            anotacoes=form.anotacoes.data,
        )
        db.session.add(projeto)
        db.session.commit()
        flash("Projeto criado com sucesso.", "success")
        return redirect(url_for("projetos.detalhe", projeto_id=projeto.id))

    return render_template("projetos/form.html", form=form, titulo="Novo projeto")


@projetos_bp.route("/<int:projeto_id>")
@login_required
def detalhe(projeto_id):
    projeto = Projeto.query.filter_by(id=projeto_id, user_id=current_user.id).first_or_404()
    checklist_form = ChecklistItemForm()
    return render_template("projetos/detalhe.html", projeto=projeto, checklist_form=checklist_form)


@projetos_bp.route("/<int:projeto_id>/editar", methods=["GET", "POST"])
@login_required
def editar(projeto_id):
    projeto = Projeto.query.filter_by(id=projeto_id, user_id=current_user.id).first_or_404()
    form = ProjetoForm(obj=projeto)

    if form.validate_on_submit():
        form.populate_obj(projeto)
        db.session.commit()
        flash("Projeto atualizado.", "success")
        return redirect(url_for("projetos.detalhe", projeto_id=projeto.id))

    return render_template("projetos/form.html", form=form, titulo="Editar projeto")


@projetos_bp.route("/<int:projeto_id>/excluir", methods=["POST"])
@login_required
def excluir(projeto_id):
    projeto = Projeto.query.filter_by(id=projeto_id, user_id=current_user.id).first_or_404()
    db.session.delete(projeto)
    db.session.commit()
    flash("Projeto excluído.", "info")
    return redirect(url_for("projetos.index"))


@projetos_bp.route("/<int:projeto_id>/checklist/novo", methods=["POST"])
@login_required
def checklist_novo(projeto_id):
    projeto = Projeto.query.filter_by(id=projeto_id, user_id=current_user.id).first_or_404()
    form = ChecklistItemForm()
    if form.validate_on_submit():
        item = ChecklistItem(projeto_id=projeto.id, texto=form.texto.data)
        db.session.add(item)
        db.session.commit()
    else:
        flash("Informe um texto para o item do checklist.", "danger")
    return redirect(url_for("projetos.detalhe", projeto_id=projeto.id))


@projetos_bp.route("/<int:projeto_id>/checklist/<int:item_id>/toggle", methods=["POST"])
@login_required
def checklist_toggle(projeto_id, item_id):
    projeto = Projeto.query.filter_by(id=projeto_id, user_id=current_user.id).first_or_404()
    item = ChecklistItem.query.filter_by(id=item_id, projeto_id=projeto.id).first_or_404()
    item.concluido = not item.concluido
    db.session.commit()
    return redirect(url_for("projetos.detalhe", projeto_id=projeto.id))


@projetos_bp.route("/<int:projeto_id>/checklist/<int:item_id>/excluir", methods=["POST"])
@login_required
def checklist_excluir(projeto_id, item_id):
    projeto = Projeto.query.filter_by(id=projeto_id, user_id=current_user.id).first_or_404()
    item = ChecklistItem.query.filter_by(id=item_id, projeto_id=projeto.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("projetos.detalhe", projeto_id=projeto.id))
