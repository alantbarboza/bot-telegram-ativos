from logging import error
import math
import yfinance as yf


def calcular_variacao(preco, media):
    if media == 0:
        return 0

    return ((preco - media) / media) * 100


def interpretar_preco(preco, media200):
    diferenca = calcular_variacao(preco, media200)

    if diferenca <= -10:
        return "🟢 O preço está bem abaixo da média de 200 dias."

    if diferenca < 0:
        return "🟢 O preço está abaixo da média de 200 dias."

    if abs(diferenca) < 0.01:
        return "⚪ O preço está praticamente na média de 200 dias."

    if diferenca <= 5:
        return "🟡 O preço está um pouco acima da média de 200 dias."

    return "🔴 O preço está acima da média de 200 dias."


def analisar(ticker):
    try:
        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )

        if df.empty:
            error(f"{ticker} retornou dados vazios.")
            return None

        close = df["Close"][ticker].dropna()

        if len(close) < 30:
            error(f"{ticker} possui histórico insuficiente.")
            return None

    except Exception as e:
        error(f"Erro ao buscar dados de {ticker}: {e}", exc_info=True)
        return None

    try:
        preco = float(close.iloc[-1])

        media30 = float(close.tail(30).mean())
        media200 = float(close.tail(min(200, len(close))).mean())

        if math.isnan(media30) or math.isnan(media200):
            return None

        variacao30 = calcular_variacao(preco, media30)
        variacao200 = calcular_variacao(preco, media200)

        return {
            "ticker": ticker.replace(".SA", ""),
            "preco": preco,
            "media30": media30,
            "media200": media200,
            "variacao30": variacao30,
            "variacao200": variacao200,
            "texto_preco": interpretar_preco(preco, media200),
        }

    except Exception as e:
        error(f"Erro no cálculo dos indicadores de {ticker}: {e}", exc_info=True)
        return None