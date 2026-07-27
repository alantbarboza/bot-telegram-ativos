from aiogram.types import Message
from asyncio import sleep, Lock
from time import time
from logging import info, warning, error
from relatorio.filtros import obter_nome_usuario
from datetime import datetime
from zoneinfo import ZoneInfo
from bot.mensagens import enviar_mensagem, mensagens
from bot.bot_instance import bot
from relatorio.envio import enviar_relatorio
import agendamento.execucao_automatica as execucao_automatica

LIMITE_MENSAGENS = 1000

comandos_em_andamento = set()

quarentena = {}
QUARENTENA_BLOQ = Lock()
TEMPO_QUARENTENA = 10

TZ = ZoneInfo("America/Sao_Paulo")
BOT_INICIADO = datetime.now(TZ)

def tempo_online():
    agora = datetime.now(TZ)
    diff = agora - BOT_INICIADO

    segundos = int(diff.total_seconds())

    minutos = segundos // 60
    horas = minutos // 60
    dias = horas // 24
    meses = dias // 30  

    if meses > 0:
        return f"{meses} meses"
    elif dias > 0:
        return f"{dias} dias"
    elif horas > 0:
        return f"{horas}h {minutos % 60}m"
    else:
        return f"{minutos}m {segundos % 60}s"

async def excluir_mensagens(chat_id):

    try:
        await sleep(2)

        for msg_id in mensagens.get(chat_id, []):

            try:

                await bot.delete_message(
                    chat_id,
                    msg_id
                )

                info(f"Mensagem apagada! chat_id: {chat_id}, message_id: {msg_id}")

                await sleep(0.1)
            except Exception as erro:
                error(f"Erro ao apagar mensagem! chat_id: {chat_id}, message_id: {msg_id}: {erro}")


        mensagens[chat_id] = []
    except Exception as erro:
        error(f"Erro ao excluir mensagens: {erro}")

async def verificar_permissao(chat_id, user_id):

    try:

        membro = await bot.get_chat_member(
            chat_id,
            user_id
        )

        return membro.status in [
            "administrator",
            "creator"
        ]

    except Exception as erro:
        error(f"Erro ao verificar permissão: {erro}")
        return False

async def verificar_quarentena(user_id):

    async with QUARENTENA_BLOQ:

        agora = time()

        if user_id in quarentena:

            ultimo_uso = quarentena[user_id]

            if agora - ultimo_uso < TEMPO_QUARENTENA:
                return True

        quarentena[user_id] = agora

        return False

async def verificar_comando(message: Message, tipo_chat: str):
    if not message.text or not message.text.startswith("/"):
        return
    
    comando = message.text.split()[0]

    if await verificar_quarentena(message.from_user.id):
        warning(
            f"Usuário {message.from_user.id} está em quarentena. "
            f"Comando '{comando}' bloqueado "
            f"no chat_id: {message.chat.id}."
        )

        return

    chave = (message.chat.id, comando)

    if chave in comandos_em_andamento:
        warning(
            f"Comando '{comando}' já está em andamento "
            f"no chat_id: {message.chat.id}. Ignorando nova execução."
        )
        return

    if tipo_chat == "supergroup":
        admin = await verificar_permissao(
            message.chat.id,
            message.from_user.id
        )

    match comando:
        case "/comandos":
            await enviar_mensagem(
                message.chat.id,
                    "Comandos disponíveis:\n"
                    "/comandos - Lista todos os comandos disponíveis.\n"
                    "/proxima_execucao - Exibe o horário previsto para enviar o relatório automaticamente.\n"
                    "/limpar - Remove as últimas 1000 mensagens.\n"
                    "/meu_id - Retorna seu user_id.\n"
                    "/online - Exibe o tempo que o bot está online.\n"
                    "/relatorio - Gera o relatório imediatamente.\n"
            )
            return
        
        case "/proxima_execucao":
            proxima = execucao_automatica.proximas_execucoes.get(str(message.from_user.id))

            if proxima:
                await enviar_mensagem(
                    message.chat.id,
                    f"Próxima execução agendada para: {proxima.strftime('%d/%m/%Y às %H:%M')}"
                )
            else:
                await enviar_mensagem(
                    message.chat.id,
                    "O agendador ainda não foi iniciado."
                )

            return

        case "/limpar":
            if tipo_chat == "supergroup" and not admin:
                await enviar_mensagem(
                    message.chat.id,
                    "Você não tem permissão para usar este comando."
                )
                return

            try:
                comandos_em_andamento.add(chave)

                await enviar_mensagem(
                    message.chat.id,
                    "Limpando mensagens..."
                )

                await excluir_mensagens(
                    message.chat.id
                )

            finally:
                comandos_em_andamento.discard(chave)

            return
 
        case "/meu_id":
            await enviar_mensagem(message.chat.id, f"Seu user_id é:\n {message.from_user.id}")

            return

        case "/online":
            await enviar_mensagem(
                message.chat.id,
                f"⏱ Bot online há: {tempo_online()}"
            )

            return

        case "/relatorio":
            if tipo_chat == "supergroup" and not admin:
                await enviar_mensagem(
                    message.chat.id,
                    "Você não tem permissão para usar este comando."
                )

                return

            for _, comando_em_execucao in comandos_em_andamento:

                if comando_em_execucao == "/relatorio":

                    await enviar_mensagem(
                        message.chat.id,
                        "O comando /relatorio já está em andamento. Tente novamente mais tarde."
                    )

                    return

            try:
                comandos_em_andamento.add(chave)

                await enviar_relatorio(message.chat.id)

            finally:
                comandos_em_andamento.discard(chave)

            return

    await enviar_mensagem( 
        message.chat.id,
            "Comando não reconhecido. Use /comandos para ver a lista de comandos disponíveis."
    )

async def salvar_mensagem(message: Message):
    nome = obter_nome_usuario(message.from_user.id)

    if message.chat.id not in mensagens:
        mensagens[message.chat.id] = []

    mensagens[message.chat.id].append(message.message_id)

    if len(mensagens[message.chat.id]) > LIMITE_MENSAGENS:
        mensagens[message.chat.id] = mensagens[message.chat.id][-LIMITE_MENSAGENS:]

    info(f"Mensagem recebida! chat: {nome}, message_id: {message.message_id}, message_text: {message.text}")