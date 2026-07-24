from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.fe import RegistroFe
from app.models.saude import RegistroSaude
from app.models.estudos import RegistroEstudo
from app.models.humor import RegistroHumor
from app.models.pureza import RegistroPureza
from app.models.jogos import RegistroJogo

historico_bp = Blueprint("historico", __name__, template_folder="../../templates/historico")

# Mapa central: cada módulo com registro diário expõe (label, ícone, model, função de resumo, endpoint de edição)
MODULOS = {
    "fe": {
        "label": "Fé",
        "icone": "bi-book",
        "model": RegistroFe,
        "editar_endpoint": "fe.editar",
        "resumo": lambda r: f"{r.livro or 'Leitura'} — {r.qtd_capitulos} capítulo(s)",
        "busca": lambda r: " ".join(filter(None, [r.livro, r.devocional, r.observacoes, r.versiculo_favorito])),
    },
    "saude": {
        "label": "Saúde",
        "icone": "bi-heart-pulse",
        "model": RegistroSaude,
        "editar_endpoint": "saude.editar",
        "resumo": lambda r: f"{(str(r.peso) + ' kg') if r.peso else 'Sem peso'}" + (f" · {r.tipo_treino}" if r.treinou and r.tipo_treino else ""),
        "busca": lambda r: " ".join(filter(None, [r.tipo_treino, r.observacoes])),
    },
    "estudos": {
        "label": "Estudos",
        "icone": "bi-mortarboard",
        "model": RegistroEstudo,
        "editar_endpoint": "estudos.editar",
        "resumo": lambda r: f"{r.tecnologia} — {r.horas}h" + (f" ({r.curso})" if r.curso else ""),
        "busca": lambda r: " ".join(filter(None, [r.tecnologia, r.curso, r.descricao, r.observacoes])),
    },
    "humor": {
        "label": "Humor",
        "icone": "bi-emoji-smile",
        "model": RegistroHumor,
        "editar_endpoint": "humor.editar",
        "resumo": lambda r: f"Humor {r.humor}/5 · Energia {r.energia}/5 · Estresse {r.estresse}/5",
        "busca": lambda r: r.observacoes or "",
    },
    "pureza": {
        "label": "Pureza",
        "icone": "bi-shield-check",
        "model": RegistroPureza,
        "editar_endpoint": "pureza.editar",
        "resumo": lambda r: "Resistiu" if r.resistiu else f"Não resistiu — {r.gatilho or 'sem gatilho registrado'}",
        "busca": lambda r: " ".join(filter(None, [r.gatilho, r.local, r.sentimento, r.observacoes])),
    },
    "jogos": {
        "label": "Jogos",
        "icone": "bi-controller",
        "model": RegistroJogo,
        "editar_endpoint": "jogos.editar",
        "resumo": lambda r: f"{r.jogo} — {r.tempo_minutos} min",
        "busca": lambda r: " ".join(filter(None, [r.jogo, r.plataforma, r.observacoes])),
    },
}


def _coletar_registros(user_id, tipo_filtro, data_inicio, data_fim, busca):
    itens = []
    tipos = [tipo_filtro] if tipo_filtro else list(MODULOS.keys())

    for tipo in tipos:
        cfg = MODULOS[tipo]
        query = cfg["model"].query.filter_by(user_id=user_id)
        if data_inicio:
            query = query.filter(cfg["model"].data >= data_inicio)
        if data_fim:
            query = query.filter(cfg["model"].data <= data_fim)

        for r in query.all():
            texto_busca = f"{cfg['resumo'](r)} {cfg['busca'](r)}".lower()
            if busca and busca.lower() not in texto_busca:
                continue
            itens.append({
                "tipo": tipo,
                "label": cfg["label"],
                "icone": cfg["icone"],
                "data": r.data,
                "resumo": cfg["resumo"](r),
                "id": r.id,
                "url_editar": url_for(cfg["editar_endpoint"], registro_id=r.id),
            })

    itens.sort(key=lambda x: x["data"], reverse=True)
    return itens


@historico_bp.route("/")
@login_required
def index():
    tipo_filtro = request.args.get("tipo", "")
    busca = request.args.get("busca", "").strip()
    data_inicio_str = request.args.get("data_inicio", "")
    data_fim_str = request.args.get("data_fim", "")
    page = request.args.get("page", 1, type=int)
    per_page = 20

    data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date() if data_inicio_str else None
    data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date() if data_fim_str else None

    todos_itens = _coletar_registros(current_user.id, tipo_filtro, data_inicio, data_fim, busca)

    total = len(todos_itens)
    inicio = (page - 1) * per_page
    itens_pagina = todos_itens[inicio: inicio + per_page]
    total_paginas = max(1, (total + per_page - 1) // per_page)

    return render_template(
        "historico/index.html",
        itens=itens_pagina,
        modulos=MODULOS,
        tipo_filtro=tipo_filtro,
        busca=busca,
        data_inicio=data_inicio_str,
        data_fim=data_fim_str,
        page=page,
        total_paginas=total_paginas,
        total=total,
    )


@historico_bp.route("/<tipo>/<int:item_id>/excluir", methods=["POST"])
@login_required
def excluir(tipo, item_id):
    cfg = MODULOS.get(tipo)
    if not cfg:
        flash("Tipo de registro inválido.", "danger")
        return redirect(url_for("historico.index"))

    registro = cfg["model"].query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(registro)
    db.session.commit()
    flash(f"Registro de {cfg['label']} excluído.", "info")
    return redirect(url_for("historico.index"))
