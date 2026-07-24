from datetime import date, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.fe import RegistroFe
from app.models.saude import RegistroSaude
from app.models.estudos import RegistroEstudo
from app.models.projetos import Projeto
from app.models.humor import RegistroHumor
from app.models.pureza import RegistroPureza
from app.models.metas import Meta
from app.models.financeiro import Transacao
from app.models.jogos import RegistroJogo

dashboard_bp = Blueprint("dashboard", __name__)


def _dias_consecutivos(registros_por_data, condicao=lambda v: True):
    """Conta a sequência atual de dias consecutivos (a partir de hoje) em que há
    registro e a condição é satisfeita."""
    dias = 0
    cursor = date.today()
    while cursor in registros_por_data and condicao(registros_por_data[cursor]):
        dias += 1
        cursor -= timedelta(days=1)
    return dias


@dashboard_bp.route("/")
@login_required
def index():
    uid = current_user.id
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)

    # ---------------- FÉ ----------------
    registros_fe = RegistroFe.query.filter_by(user_id=uid).all()
    fe_por_data = {r.data: r for r in registros_fe}
    fe_semana = [r for r in registros_fe if r.data >= inicio_semana]
    dias_consecutivos_fe = _dias_consecutivos(fe_por_data)

    # ---------------- SAÚDE ----------------
    registros_saude = RegistroSaude.query.filter_by(user_id=uid).order_by(RegistroSaude.data.asc()).all()
    saude_semana = [r for r in registros_saude if r.data >= inicio_semana]
    pesos = [r for r in registros_saude if r.peso]
    peso_atual = pesos[-1].peso if pesos else None

    # ---------------- ESTUDOS ----------------
    registros_estudo = RegistroEstudo.query.filter_by(user_id=uid).all()
    horas_estudo_semana = sum(r.horas for r in registros_estudo if r.data >= inicio_semana)

    # ---------------- PROJETOS ----------------
    projetos = Projeto.query.filter_by(user_id=uid).all()
    projetos_ativos = sum(1 for p in projetos if p.status == "em_andamento")
    projetos_atrasados = sum(1 for p in projetos if p.atrasado)

    # ---------------- HUMOR ----------------
    registros_humor = RegistroHumor.query.filter_by(user_id=uid).order_by(RegistroHumor.data.desc()).all()
    humor_hoje = next((r for r in registros_humor if r.data == hoje), None)

    # ---------------- PUREZA ----------------
    registros_pureza = RegistroPureza.query.filter_by(user_id=uid).all()
    pureza_por_data = {r.data: r.resistiu for r in registros_pureza}
    dias_consecutivos_pureza = _dias_consecutivos(pureza_por_data, condicao=lambda resistiu: resistiu)

    # ---------------- METAS ----------------
    metas = Meta.query.filter_by(user_id=uid).all()
    metas_em_andamento = sum(1 for m in metas if m.status == "em_andamento")
    metas_concluidas = sum(1 for m in metas if m.status == "concluida")

    # ---------------- FINANCEIRO ----------------
    transacoes = Transacao.query.filter_by(user_id=uid).all()
    saldo = sum(t.valor_assinado for t in transacoes)
    transacoes_mes = [t for t in transacoes if t.data >= inicio_mes]
    receitas_mes = sum(t.valor for t in transacoes_mes if t.tipo == "receita")
    despesas_mes = sum(t.valor for t in transacoes_mes if t.tipo == "despesa")

    # ---------------- JOGOS ----------------
    registros_jogo = RegistroJogo.query.filter_by(user_id=uid).all()
    tempo_jogo_hoje = sum(r.tempo_minutos for r in registros_jogo if r.data == hoje)

    cards = {
        "dias_consecutivos_fe": dias_consecutivos_fe,
        "capitulos_semana": sum(r.qtd_capitulos for r in fe_semana),
        "peso_atual": peso_atual,
        "treinos_semana": sum(1 for r in saude_semana if r.treinou),
        "horas_estudo_semana": round(horas_estudo_semana, 1),
        "projetos_ativos": projetos_ativos,
        "projetos_atrasados": projetos_atrasados,
        "humor_hoje": humor_hoje.humor if humor_hoje else None,
        "dias_consecutivos_pureza": dias_consecutivos_pureza,
        "metas_em_andamento": metas_em_andamento,
        "metas_concluidas": metas_concluidas,
        "saldo": saldo,
        "receitas_mes": receitas_mes,
        "despesas_mes": despesas_mes,
        "tempo_jogo_hoje": tempo_jogo_hoje,
    }

    # Série dos últimos 7 dias (capítulos lidos por dia) para o gráfico de Fé
    labels, valores = [], []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        registro = fe_por_data.get(dia)
        labels.append(dia.strftime("%d/%m"))
        valores.append(registro.qtd_capitulos if registro else 0)

    # Últimos registros entre TODOS os módulos, para o feed de atividade recente
    from app.blueprints.historico.routes import _coletar_registros
    ultimos_registros = _coletar_registros(uid, tipo_filtro="", data_inicio=None, data_fim=None, busca="")[:8]

    return render_template(
        "dashboard/index.html",
        cards=cards,
        ultimos_registros=ultimos_registros,
        grafico_labels=labels,
        grafico_valores=valores,
    )
