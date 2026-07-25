from asyncio import to_thread
from logging import error, info

from bot.mensagens import enviar_mensagem
from relatorio.analise import analisar
from relatorio.filtros import obter_ativos


def formatar_relatorio(resultado):

    return (
        f"📊 {resultado['ticker']}\n\n"

        f"💰 Preço atual\n"
        f"R$ {resultado['preco']:.2f}\n\n"

        f"📈 Comparação com o histórico\n"
        f"{resultado['texto_media']}\n"
        f"Preço médio dos últimos meses: "
        f"R$ {resultado['media200']:.2f}\n\n"

        f"📉 Distância do maior preço recente\n"
        f"{resultado['texto_queda']}\n"
        f"{resultado['queda90']:.2f}% abaixo do pico dos últimos 90 dias.\n\n"

        f"📊 Movimento recente\n"
        f"{resultado['texto_rsi']}\n"
        f"RSI: {resultado['rsi']:.1f}\n\n"

        f"⭐ Nota geral: {resultado['score']}/100\n"
        f"{resultado['status']}"
    )


async def enviar_relatorio(chat_id):

    try:

        await enviar_mensagem(
            chat_id,
            "📊 Gerando relatório..."
        )

        texto_final = ""

        ativos = obter_ativos(chat_id)

        for ativo in ativos:

            resultado = await to_thread(
                analisar,
                ativo
            )

            if resultado is None:
                info(f"Não foi possível analisar {ativo}.")
                continue

            texto_final += formatar_relatorio(resultado)
            texto_final += "\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

        if not texto_final:
            texto_final = "Não foi possível gerar o relatório."

        await enviar_mensagem(chat_id, texto_final)

        info(f"Relatório enviado para {chat_id}")

    except Exception as erro:

        error(f"Erro ao enviar relatório: {erro}")

        await enviar_mensagem(
            chat_id,
            "❌ Erro ao gerar o relatório."
        )