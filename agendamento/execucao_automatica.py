from asyncio import sleep, create_task
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from logging import info
from relatorio.envio import enviar_relatorio
from relatorio.filtros import carregar_usuarios, obter_proxima_execucao, salvar_proxima_execucao
import bot.comandos as comandos

TZ = ZoneInfo("America/Sao_Paulo")

proximas_execucoes = {}

async def agendar_usuario(chat_id):
    global proximas_execucoes

    while True:

        agora = datetime.now(TZ)

        data_salva = obter_proxima_execucao(chat_id)

        if not data_salva:
            info(f"{chat_id} não possui próxima execução cadastrada.")
            return

        proxima_execucao = datetime.fromisoformat(data_salva)

        if proxima_execucao <= agora:

            chave = (0, "/relatorio")

            relatorio_em_andamento = False

            for _, comando in comandos.comandos_em_andamento:

                if comando == "/relatorio":
                    relatorio_em_andamento = True
                    break

            if not relatorio_em_andamento:

                try:

                    comandos.comandos_em_andamento.add(chave)

                    info(f"Iniciando execução automática para {chat_id}.")

                    await enviar_relatorio(chat_id)

                    info(f"Execução automática para {chat_id} finalizada.")

                finally:
                    comandos.comandos_em_andamento.discard(chave)

            agora = datetime.now(TZ)

            proxima_execucao = (
                agora.replace(minute=0, second=0, microsecond=0)
                + timedelta(hours=1)
            )

            salvar_proxima_execucao(chat_id, proxima_execucao)

        proximas_execucoes[str(chat_id)] = proxima_execucao

        segundos = max((proxima_execucao - datetime.now(TZ)).total_seconds(), 0)

        info(f"Próxima execução de {chat_id}: {proxima_execucao}")

        await sleep(segundos)

        chave = (0, "/relatorio")

        relatorio_em_andamento = False

        for _, comando in comandos.comandos_em_andamento:

            if comando == "/relatorio":
                relatorio_em_andamento = True
                break

        if relatorio_em_andamento:
            info(
                f"Execução automática de {chat_id} ignorada "
                f"porque já existe um relatório em andamento."
            )
            continue

        try:

            comandos.comandos_em_andamento.add(chave)

            info(f"Iniciando execução automática para {chat_id}.")

            await enviar_relatorio(chat_id)

            info(f"Execução automática para {chat_id} finalizada.")

        finally:
            comandos.comandos_em_andamento.discard(chave)

        agora = datetime.now(TZ)

        proxima_execucao = (
            agora.replace(minute=0, second=0, microsecond=0)
            + timedelta(hours=1)
        )

        proximas_execucoes[str(chat_id)] = proxima_execucao

        salvar_proxima_execucao(chat_id, proxima_execucao)


async def iniciar_agendador():
    usuarios = carregar_usuarios()

    for chat_id in usuarios:
        create_task(agendar_usuario(int(chat_id)))

    info("Agendador iniciado.")

    while True:
        await sleep(3600)