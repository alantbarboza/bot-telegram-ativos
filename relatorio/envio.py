from asyncio import to_thread
from logging import error, info
from bot.mensagens import enviar_mensagem
from relatorio.analise import analisar
from relatorio.filtros import obter_ativos

def formatar_relatorio(resultado):
    return (
        f"📊 {resultado['ticker']}\n\n"

        f"💰 Preço atual: R$ {resultado['preco']:.2f}\n\n"

        f"📈 Preço máximo do pregão atual: R$ {resultado['preco_maximo']:.2f}\n"
        f"📉 Preço mínimo do pregão atual: R$ {resultado['preco_minimo']:.2f}\n\n"

        f"Preço médio:\n"
        f"30 dias: R$ {resultado['media30']:.2f}\n"
        f"200 dias: R$ {resultado['media200']:.2f}\n\n"

        f"Diferença: Preço atual X Preço médio\n"
        f"30 dias: {resultado['variacao30']:+.2f}%\n"
        f"200 dias: {resultado['variacao200']:+.2f}%\n\n"

        f"Análise:\n"
        f"{resultado['texto_preco']}\n\n"
    )


async def enviar_relatorio(chat_id):
    try:
        await enviar_mensagem(chat_id, "📊 Gerando relatório...")

        texto_final = ""
        ativos = obter_ativos(chat_id)

        for ativo in ativos:
            resultado = await to_thread(analisar, ativo)

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
        await enviar_mensagem(chat_id, "Erro ao gerar o relatório.")