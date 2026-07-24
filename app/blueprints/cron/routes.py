from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from flask import Blueprint, jsonify, request, current_app
from app.extensions import db
from app.models.lembretes import Lembrete
from app.models.user import User
from app.utils.telegram import enviar_telegram

cron_bp = Blueprint("cron", __name__)

# Tolerância: um lembrete marcado para HH:MM dispara se o horário atual estiver
# dentro dessa janela, para acomodar agendadores externos que rodam a cada N minutos.
TOLERANCIA_MINUTOS = 6


@cron_bp.route("/cron/lembretes")
def disparar_lembretes():
    secret_configurado = current_app.config.get("CRON_SECRET")

    # A Vercel envia "Authorization: Bearer <CRON_SECRET>" automaticamente quando
    # a env var CRON_SECRET está configurada no projeto. Um agendador externo
    # (ex: cron-job.org) geralmente é mais simples de configurar via query param.
    auth_header = request.headers.get("Authorization", "")
    secret_via_header = auth_header.replace("Bearer ", "", 1) if auth_header.startswith("Bearer ") else ""
    secret_via_query = request.args.get("secret", "")
    secret_recebido = secret_via_header or secret_via_query

    if secret_configurado and secret_recebido != secret_configurado:
        return jsonify({"erro": "não autorizado"}), 401

    tz = ZoneInfo(current_app.config.get("TIMEZONE", "America/Sao_Paulo"))
    agora = datetime.now(tz)
    hoje = agora.date()
    dia_semana_atual = str(agora.weekday())  # 0=segunda ... 6=domingo

    enviados, ignorados, erros = [], [], []

    lembretes = Lembrete.query.filter_by(ativo=True).all()
    for lembrete in lembretes:
        if dia_semana_atual not in lembrete.dias_semana.split(","):
            continue
        if lembrete.ultimo_disparo == hoje:
            continue

        horario_lembrete = datetime.combine(hoje, lembrete.hora, tzinfo=tz)
        diferenca_minutos = abs((agora - horario_lembrete).total_seconds()) / 60
        if diferenca_minutos > TOLERANCIA_MINUTOS:
            continue

        user = User.query.get(lembrete.user_id)
        if not user or not user.telegram_chat_id:
            ignorados.append({"lembrete_id": lembrete.id, "motivo": "usuário sem Telegram configurado"})
            continue

        ok, detalhe = enviar_telegram(user.telegram_chat_id, lembrete.texto_notificacao())
        if ok:
            lembrete.ultimo_disparo = hoje
            db.session.commit()
            enviados.append({"lembrete_id": lembrete.id, "titulo": lembrete.titulo})
        else:
            erros.append({"lembrete_id": lembrete.id, "erro": detalhe})

    return jsonify({
        "horario_verificado": agora.isoformat(),
        "enviados": enviados,
        "ignorados": ignorados,
        "erros": erros,
    })
