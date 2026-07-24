from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.metas import Meta, CATEGORIA_META_CHOICES, STATUS_META_CHOICES
from app.blueprints.metas.forms import MetaForm

metas_bp = Blueprint("metas", __name__, template_folder="../../templates/metas")


def _auto_concluir(meta):
    """Marca a meta como concluída automaticamente quando o valor atual atinge a meta."""
    if meta.status == "em_andamento" and meta.valor_final and meta.valor_atual >= meta.valor_final:
        meta.status = "concluida"


@metas_bp.route("/")
@login_required
def index():
    categoria_filtro = request.args.get("categoria", "")
    status_filtro = request.args.get("status", "")

    query = Meta.query.filter_by(user_id=current_user.id)
    if categoria_filtro:
        query = query.filter_by(categoria=categoria_filtro)
    if status_filtro:
        query = query.filter_by(status=status_filtro)

    metas = query.order_by(Meta.prazo.asc().nullslast(), Meta.criado_em.desc()).all()

    todas = Meta.query.filter_by(user_id=current_user.id).all()
    stats = {
        "total": len(todas),
        "em_andamento": sum(1 for m in todas if m.status == "em_andamento"),
        "concluidas": sum(1 for m in todas if m.status == "concluida"),
        "atrasadas": sum(1 for m in todas if m.atrasada),
    }

    return render_template(
        "metas/index.html",
        metas=metas,
        stats=stats,
        categoria_choices=CATEGORIA_META_CHOICES,
        status_choices=STATUS_META_CHOICES,
        categoria_filtro=categoria_filtro,
        status_filtro=status_filtro,
    )


@metas_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = MetaForm(categoria="pessoal", status="em_andamento")
    if form.validate_on_submit():
        meta = Meta(
            user_id=current_user.id,
            titulo=form.titulo.data,
            categoria=form.categoria.data,
            objetivo=form.objetivo.data,
            valor_atual=form.valor_atual.data or 0,
            valor_final=form.valor_final.data,
            prazo=form.prazo.data,
            status=form.status.data,
        )
        _auto_concluir(meta)
        db.session.add(meta)
        db.session.commit()
        flash("Meta criada com sucesso.", "success")
        return redirect(url_for("metas.index"))

    return render_template("metas/form.html", form=form, titulo="Nova meta")


@metas_bp.route("/<int:meta_id>/editar", methods=["GET", "POST"])
@login_required
def editar(meta_id):
    meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first_or_404()
    form = MetaForm(obj=meta)

    if form.validate_on_submit():
        form.populate_obj(meta)
        _auto_concluir(meta)
        db.session.commit()
        flash("Meta atualizada.", "success")
        return redirect(url_for("metas.index"))

    return render_template("metas/form.html", form=form, titulo="Editar meta")


@metas_bp.route("/<int:meta_id>/excluir", methods=["POST"])
@login_required
def excluir(meta_id):
    meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first_or_404()
    db.session.delete(meta)
    db.session.commit()
    flash("Meta excluída.", "info")
    return redirect(url_for("metas.index"))
