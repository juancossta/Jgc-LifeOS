from datetime import date
from calendar import month_name
from types import SimpleNamespace
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.financeiro import (
    CategoriaFinanceira, Transacao, ObjetivoFinanceiro, Investimento
)
from app.blueprints.financeiro.forms import (
    TransacaoForm, CategoriaFinanceiraForm, ObjetivoFinanceiroForm, InvestimentoForm
)

financeiro_bp = Blueprint("financeiro", __name__, template_folder="../../templates/financeiro")


def _popular_categorias(form, tipo=None):
    query = CategoriaFinanceira.query.filter_by(user_id=current_user.id)
    if tipo:
        query = query.filter_by(tipo=tipo)
    categorias = query.order_by(CategoriaFinanceira.nome).all()
    form.categoria_id.choices = [(0, "Sem categoria")] + [(c.id, c.nome) for c in categorias]


# --------------------------- DASHBOARD ---------------------------

@financeiro_bp.route("/")
@login_required
def index():
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)

    todas = Transacao.query.filter_by(user_id=current_user.id).all()
    saldo = sum(t.valor_assinado for t in todas)

    do_mes = [t for t in todas if t.data >= inicio_mes]
    receitas_mes = sum(t.valor for t in do_mes if t.tipo == "receita")
    despesas_mes = sum(t.valor for t in do_mes if t.tipo == "despesa")

    # gráfico: despesas por categoria (mês atual)
    despesas_por_categoria = {}
    for t in do_mes:
        if t.tipo != "despesa":
            continue
        nome_cat = t.categoria.nome if t.categoria else "Sem categoria"
        despesas_por_categoria[nome_cat] = despesas_por_categoria.get(nome_cat, 0) + t.valor

    # gráfico: evolução dos últimos 6 meses
    labels_evolucao, receitas_evolucao, despesas_evolucao = [], [], []
    for i in range(5, -1, -1):
        mes_ref = (hoje.replace(day=1) - relativedelta(months=i))
        mes_seguinte = mes_ref + relativedelta(months=1)
        do_periodo = [t for t in todas if mes_ref <= t.data < mes_seguinte]
        labels_evolucao.append(f"{month_name[mes_ref.month][:3].capitalize()}/{str(mes_ref.year)[2:]}")
        receitas_evolucao.append(sum(t.valor for t in do_periodo if t.tipo == "receita"))
        despesas_evolucao.append(sum(t.valor for t in do_periodo if t.tipo == "despesa"))

    ultimas = (
        Transacao.query.filter_by(user_id=current_user.id)
        .order_by(Transacao.data.desc(), Transacao.criado_em.desc())
        .limit(8)
        .all()
    )

    objetivos = (
        ObjetivoFinanceiro.query.filter_by(user_id=current_user.id)
        .order_by(ObjetivoFinanceiro.prazo.asc().nullslast())
        .limit(4)
        .all()
    )

    total_investido = sum(i.valor_investido for i in Investimento.query.filter_by(user_id=current_user.id))
    total_atual_investimentos = sum(i.valor_atual for i in Investimento.query.filter_by(user_id=current_user.id))

    return render_template(
        "financeiro/index.html",
        saldo=saldo,
        receitas_mes=receitas_mes,
        despesas_mes=despesas_mes,
        ultimas=ultimas,
        objetivos=objetivos,
        total_investido=total_investido,
        total_atual_investimentos=total_atual_investimentos,
        cat_labels=list(despesas_por_categoria.keys()),
        cat_valores=list(despesas_por_categoria.values()),
        evol_labels=labels_evolucao,
        evol_receitas=receitas_evolucao,
        evol_despesas=despesas_evolucao,
    )


# --------------------------- TRANSAÇÕES ---------------------------

@financeiro_bp.route("/transacoes")
@login_required
def transacoes():
    tipo_filtro = request.args.get("tipo", "")
    page = request.args.get("page", 1, type=int)

    query = Transacao.query.filter_by(user_id=current_user.id)
    if tipo_filtro in ("receita", "despesa"):
        query = query.filter_by(tipo=tipo_filtro)

    pagination = query.order_by(Transacao.data.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("financeiro/transacoes.html", pagination=pagination, tipo_filtro=tipo_filtro)


@financeiro_bp.route("/transacoes/novo", methods=["GET", "POST"])
@login_required
def transacao_nova():
    form = TransacaoForm(obj=SimpleNamespace(tipo="despesa", data=date.today()))
    _popular_categorias(form)

    if form.validate_on_submit():
        transacao = Transacao(
            user_id=current_user.id,
            tipo=form.tipo.data,
            valor=form.valor.data,
            data=form.data.data,
            categoria_id=form.categoria_id.data or None,
            descricao=form.descricao.data,
        )
        db.session.add(transacao)
        db.session.commit()
        flash("Transação registrada.", "success")
        return redirect(url_for("financeiro.transacoes"))

    return render_template("financeiro/transacao_form.html", form=form, titulo="Nova transação")


@financeiro_bp.route("/transacoes/<int:transacao_id>/editar", methods=["GET", "POST"])
@login_required
def transacao_editar(transacao_id):
    transacao = Transacao.query.filter_by(id=transacao_id, user_id=current_user.id).first_or_404()
    form = TransacaoForm(obj=transacao)
    form.categoria_id.data = transacao.categoria_id or 0
    _popular_categorias(form)

    if form.validate_on_submit():
        transacao.tipo = form.tipo.data
        transacao.valor = form.valor.data
        transacao.data = form.data.data
        transacao.categoria_id = form.categoria_id.data or None
        transacao.descricao = form.descricao.data
        db.session.commit()
        flash("Transação atualizada.", "success")
        return redirect(url_for("financeiro.transacoes"))

    return render_template("financeiro/transacao_form.html", form=form, titulo="Editar transação")


@financeiro_bp.route("/transacoes/<int:transacao_id>/excluir", methods=["POST"])
@login_required
def transacao_excluir(transacao_id):
    transacao = Transacao.query.filter_by(id=transacao_id, user_id=current_user.id).first_or_404()
    db.session.delete(transacao)
    db.session.commit()
    flash("Transação excluída.", "info")
    return redirect(url_for("financeiro.transacoes"))


# --------------------------- CATEGORIAS ---------------------------

@financeiro_bp.route("/categorias", methods=["GET", "POST"])
@login_required
def categorias():
    form = CategoriaFinanceiraForm()
    if form.validate_on_submit():
        existente = CategoriaFinanceira.query.filter_by(
            user_id=current_user.id, nome=form.nome.data.strip(), tipo=form.tipo.data
        ).first()
        if existente:
            flash("Você já possui uma categoria com esse nome e tipo.", "danger")
        else:
            db.session.add(CategoriaFinanceira(user_id=current_user.id, nome=form.nome.data.strip(), tipo=form.tipo.data))
            db.session.commit()
            flash("Categoria adicionada.", "success")
        return redirect(url_for("financeiro.categorias"))

    lista = CategoriaFinanceira.query.filter_by(user_id=current_user.id).order_by(CategoriaFinanceira.tipo, CategoriaFinanceira.nome).all()
    return render_template("financeiro/categorias.html", form=form, categorias=lista)


@financeiro_bp.route("/categorias/<int:categoria_id>/excluir", methods=["POST"])
@login_required
def categoria_excluir(categoria_id):
    categoria = CategoriaFinanceira.query.filter_by(id=categoria_id, user_id=current_user.id).first_or_404()
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoria removida. As transações associadas ficaram sem categoria.", "info")
    return redirect(url_for("financeiro.categorias"))


# --------------------------- OBJETIVOS FINANCEIROS ---------------------------

@financeiro_bp.route("/objetivos")
@login_required
def objetivos():
    lista = ObjetivoFinanceiro.query.filter_by(user_id=current_user.id).order_by(ObjetivoFinanceiro.prazo.asc().nullslast()).all()
    return render_template("financeiro/objetivos.html", objetivos=lista)


@financeiro_bp.route("/objetivos/novo", methods=["GET", "POST"])
@login_required
def objetivo_novo():
    form = ObjetivoFinanceiroForm()
    if form.validate_on_submit():
        objetivo = ObjetivoFinanceiro(
            user_id=current_user.id,
            titulo=form.titulo.data,
            valor_atual=form.valor_atual.data or 0,
            valor_meta=form.valor_meta.data,
            prazo=form.prazo.data,
        )
        db.session.add(objetivo)
        db.session.commit()
        flash("Objetivo financeiro criado.", "success")
        return redirect(url_for("financeiro.objetivos"))
    return render_template("financeiro/objetivo_form.html", form=form, titulo="Novo objetivo")


@financeiro_bp.route("/objetivos/<int:objetivo_id>/editar", methods=["GET", "POST"])
@login_required
def objetivo_editar(objetivo_id):
    objetivo = ObjetivoFinanceiro.query.filter_by(id=objetivo_id, user_id=current_user.id).first_or_404()
    form = ObjetivoFinanceiroForm(obj=objetivo)
    if form.validate_on_submit():
        form.populate_obj(objetivo)
        db.session.commit()
        flash("Objetivo atualizado.", "success")
        return redirect(url_for("financeiro.objetivos"))
    return render_template("financeiro/objetivo_form.html", form=form, titulo="Editar objetivo")


@financeiro_bp.route("/objetivos/<int:objetivo_id>/excluir", methods=["POST"])
@login_required
def objetivo_excluir(objetivo_id):
    objetivo = ObjetivoFinanceiro.query.filter_by(id=objetivo_id, user_id=current_user.id).first_or_404()
    db.session.delete(objetivo)
    db.session.commit()
    flash("Objetivo excluído.", "info")
    return redirect(url_for("financeiro.objetivos"))


# --------------------------- INVESTIMENTOS ---------------------------

@financeiro_bp.route("/investimentos")
@login_required
def investimentos():
    lista = Investimento.query.filter_by(user_id=current_user.id).order_by(Investimento.data_aplicacao.desc()).all()
    total_investido = sum(i.valor_investido for i in lista)
    total_atual = sum(i.valor_atual for i in lista)
    return render_template(
        "financeiro/investimentos.html", investimentos=lista,
        total_investido=total_investido, total_atual=total_atual
    )


@financeiro_bp.route("/investimentos/novo", methods=["GET", "POST"])
@login_required
def investimento_novo():
    form = InvestimentoForm(tipo="renda_fixa", data_aplicacao=date.today())
    if form.validate_on_submit():
        investimento = Investimento(
            user_id=current_user.id,
            nome=form.nome.data,
            tipo=form.tipo.data,
            valor_investido=form.valor_investido.data,
            valor_atual=form.valor_atual.data,
            data_aplicacao=form.data_aplicacao.data,
            observacoes=form.observacoes.data,
        )
        db.session.add(investimento)
        db.session.commit()
        flash("Investimento registrado.", "success")
        return redirect(url_for("financeiro.investimentos"))
    return render_template("financeiro/investimento_form.html", form=form, titulo="Novo investimento")


@financeiro_bp.route("/investimentos/<int:investimento_id>/editar", methods=["GET", "POST"])
@login_required
def investimento_editar(investimento_id):
    investimento = Investimento.query.filter_by(id=investimento_id, user_id=current_user.id).first_or_404()
    form = InvestimentoForm(obj=investimento)
    if form.validate_on_submit():
        form.populate_obj(investimento)
        db.session.commit()
        flash("Investimento atualizado.", "success")
        return redirect(url_for("financeiro.investimentos"))
    return render_template("financeiro/investimento_form.html", form=form, titulo="Editar investimento")


@financeiro_bp.route("/investimentos/<int:investimento_id>/excluir", methods=["POST"])
@login_required
def investimento_excluir(investimento_id):
    investimento = Investimento.query.filter_by(id=investimento_id, user_id=current_user.id).first_or_404()
    db.session.delete(investimento)
    db.session.commit()
    flash("Investimento excluído.", "info")
    return redirect(url_for("financeiro.investimentos"))
