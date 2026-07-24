from datetime import date, timedelta
from types import SimpleNamespace
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.saude import RegistroSaude
from app.models.humor import RegistroHumor
from app.models.metas import Meta
from app.blueprints.saude.forms import RegistroSaudeForm

saude_bp = Blueprint("saude", __name__, template_folder="../../templates/saude")


def _dias_consecutivos(registros_por_data, condicao):
    dias = 0
    cursor = date.today()
    while cursor in registros_por_data and condicao(registros_por_data[cursor]):
        dias += 1
        cursor -= timedelta(days=1)
    return dias


@saude_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = (
        RegistroSaude.query.filter_by(user_id=current_user.id)
        .order_by(RegistroSaude.data.desc())
        .paginate(page=page, per_page=15, error_out=False)
    )

    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())

    todos = RegistroSaude.query.filter_by(user_id=current_user.id).order_by(RegistroSaude.data.asc()).all()
    da_semana = [r for r in todos if r.data >= inicio_semana]

    pesos_registrados = [r for r in todos if r.peso]
    peso_atual = pesos_registrados[-1].peso if pesos_registrados else None
    peso_inicial = pesos_registrados[0].peso if pesos_registrados else None
    variacao_peso = round(peso_atual - peso_inicial, 1) if (peso_atual and peso_inicial) else None

    imc_atual = current_user.calcular_imc(peso_atual) if peso_atual else None
    imc_classificacao = current_user.classificar_imc(imc_atual)

    meta_agua = current_user.meta_agua_ml or 2000
    meta_sono = current_user.meta_sono_horas or 7
    registros_por_data = {r.data: r for r in todos}
    dias_consecutivos_agua = _dias_consecutivos(registros_por_data, lambda r: (r.agua_ml or 0) >= meta_agua)
    dias_consecutivos_sono = _dias_consecutivos(registros_por_data, lambda r: (r.sono_horas or 0) >= meta_sono)

    # Correlação treino x humor: média de humor nos dias que treinou vs. não treinou
    registros_humor = RegistroHumor.query.filter_by(user_id=current_user.id).all()
    humor_por_data = {r.data: r.humor for r in registros_humor}
    humor_treinou, humor_nao_treinou = [], []
    for r in todos:
        h = humor_por_data.get(r.data)
        if h is None:
            continue
        (humor_treinou if r.treinou else humor_nao_treinou).append(h)
    correlacao = {
        "media_humor_treino": round(sum(humor_treinou) / len(humor_treinou), 1) if humor_treinou else None,
        "media_humor_sem_treino": round(sum(humor_nao_treinou) / len(humor_nao_treinou), 1) if humor_nao_treinou else None,
        "amostras_suficientes": len(humor_treinou) >= 3 and len(humor_nao_treinou) >= 3,
    }

    # Metas de saúde vinculadas (categoria = saude no módulo Metas)
    metas_saude = Meta.query.filter_by(user_id=current_user.id, categoria="saude", status="em_andamento").all()

    stats = {
        "peso_atual": peso_atual,
        "variacao_peso": variacao_peso,
        "imc_atual": imc_atual,
        "imc_classificacao": imc_classificacao,
        "media_sono_semana": round(sum(r.sono_horas or 0 for r in da_semana) / len(da_semana), 1) if da_semana else 0,
        "media_agua_semana": round(sum(r.agua_ml or 0 for r in da_semana) / len(da_semana)) if da_semana else 0,
        "treinos_semana": sum(1 for r in da_semana if r.treinou),
        "total_registros": len(todos),
        "dias_consecutivos_agua": dias_consecutivos_agua,
        "dias_consecutivos_sono": dias_consecutivos_sono,
        "meta_agua": meta_agua,
        "meta_sono": meta_sono,
    }

    # Últimos 30 registros com peso: valor bruto + média móvel de 7 dias
    ultimos_pesos = [r for r in todos if r.peso][-30:]
    peso_labels = [r.data.strftime("%d/%m") for r in ultimos_pesos]
    peso_valores = [r.peso for r in ultimos_pesos]
    peso_media_movel = []
    for i in range(len(ultimos_pesos)):
        janela = [r.peso for r in ultimos_pesos[max(0, i - 6): i + 1]]
        peso_media_movel.append(round(sum(janela) / len(janela), 1))

    return render_template(
        "saude/index.html",
        pagination=pagination,
        stats=stats,
        correlacao=correlacao,
        metas_saude=metas_saude,
        peso_labels=peso_labels,
        peso_valores=peso_valores,
        peso_media_movel=peso_media_movel,
    )


@saude_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = RegistroSaudeForm(obj=SimpleNamespace(data=date.today()))
    if form.validate_on_submit():
        registro = RegistroSaude(
            user_id=current_user.id,
            data=form.data.data,
            peso=form.peso.data,
            agua_ml=form.agua_ml.data or 0,
            sono_horas=form.sono_horas.data or 0,
            treinou=form.treinou.data,
            tipo_treino=form.tipo_treino.data if form.treinou.data else None,
            cardio_min=form.cardio_min.data or 0,
            passos=form.passos.data or 0,
            observacoes=form.observacoes.data,
        )
        db.session.add(registro)
        db.session.commit()
        flash("Registro de saúde salvo com sucesso.", "success")
        return redirect(url_for("saude.index"))

    return render_template("saude/form.html", form=form, titulo="Novo registro")


@saude_bp.route("/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(registro_id):
    registro = RegistroSaude.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    form = RegistroSaudeForm(obj=registro)

    if form.validate_on_submit():
        registro.data = form.data.data
        registro.peso = form.peso.data
        registro.agua_ml = form.agua_ml.data or 0
        registro.sono_horas = form.sono_horas.data or 0
        registro.treinou = form.treinou.data
        registro.tipo_treino = form.tipo_treino.data if form.treinou.data else None
        registro.cardio_min = form.cardio_min.data or 0
        registro.passos = form.passos.data or 0
        registro.observacoes = form.observacoes.data
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("saude.index"))

    return render_template("saude/form.html", form=form, titulo="Editar registro")


@saude_bp.route("/<int:registro_id>/excluir", methods=["POST"])
@login_required
def excluir(registro_id):
    registro = RegistroSaude.query.filter_by(id=registro_id, user_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash("Registro excluído.", "info")
    return redirect(url_for("saude.index"))
