from logging import error
import math
import yfinance as yf


def calcular_rsi(close, periodo=14):
    """
    Calcula o RSI (Relative Strength Index).

    O RSI varia de 0 a 100.

    Quanto menor o RSI, maior foi a pressão de venda recentemente.
    Quanto maior o RSI, maior foi a pressão de compra.
    """

    delta = close.diff()

    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)

    media_ganho = ganho.rolling(periodo).mean()
    media_perda = perda.rolling(periodo).mean()

    rs = media_ganho / media_perda

    return 100 - (100 / (1 + rs))


def pontuacao_preco_vs_media(preco, media):
    """
    Retorna uma pontuação de 0 a 50.

    Quanto mais abaixo da média estiver,
    maior será a pontuação.
    """

    diferenca = ((media - preco) / media) * 100

    if diferenca <= 0:
        return 0

    return min(diferenca * 5, 50)


def pontuacao_desconto(queda):
    """
    Retorna uma pontuação de 0 a 25.

    Quanto maior a queda em relação ao maior preço
    dos últimos 90 dias, maior a pontuação.
    """

    return min(max(queda, 0), 25)


def pontuacao_movimento(rsi):
    """
    Retorna uma pontuação de 0 a 25.

    RSI baixo indica que houve muitas quedas recentemente.

    Isso NÃO garante que irá subir,
    apenas indica que pode estar barato.
    """

    if rsi <= 30:
        return 25

    if rsi >= 70:
        return 0

    return (70 - rsi) / 40 * 25


def interpretar_media(preco, media):

    diferenca = ((preco - media) / media) * 100

    if diferenca <= -5:
        return "🟢 Bem abaixo da média histórica."

    if diferenca < 0:
        return "🟢 Um pouco abaixo da média."

    if diferenca <= 5:
        return "🟡 Um pouco acima da média."

    return "🔴 Bem acima da média."


def interpretar_queda(queda):

    if queda >= 20:
        return "🟢 Está bem abaixo do maior preço recente."

    if queda >= 10:
        return "🟡 Está abaixo do maior preço recente."

    return "🔴 Está próximo do maior preço recente."


def interpretar_rsi(rsi):

    if rsi <= 30:
        return "🟢 Caiu bastante recentemente."

    if rsi < 50:
        return "🟡 Movimento levemente de baixa."

    if rsi < 70:
        return "🟡 Movimento neutro."

    return "🔴 Subiu bastante recentemente."


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
        high = df["High"][ticker].dropna()

        if len(close) < 30:
            error(f"{ticker} possui apenas {len(close)} dias de histórico.")
            return None

    except Exception as e:
        error(f"Erro ao buscar dados de {ticker}: {e}", exc_info=True)
        return None

    try:

        preco = float(close.iloc[-1])

        media30 = float(close.tail(30).mean())
        media200 = float(close.tail(200).mean())

        maxima90 = float(high.tail(90).max())

        if maxima90 == 0:
            return None

        queda90 = (maxima90 - preco) / maxima90 * 100

        rsi = calcular_rsi(close).iloc[-1]

        if math.isnan(rsi):
            rsi = 50

        rsi = float(rsi)

        score = round(
            pontuacao_preco_vs_media(preco, media200)
            + pontuacao_desconto(queda90)
            + pontuacao_movimento(rsi)
            + pontuacao_preco_vs_media(preco, media30)
        )

        score = min(score, 100)

        if score >= 80:
            status = "🟢 Excelente oportunidade"

        elif score >= 60:
            status = "🟢 Boa oportunidade"

        elif score >= 40:
            status = "🟡 Oportunidade moderada"

        elif score >= 20:
            status = "🟠 Pouca oportunidade"

        else:
            status = "🔴 Melhor aguardar."

        return {

            "ticker": ticker.replace(".SA", ""),

            "preco": preco,

            "media30": media30,

            "media200": media200,

            "queda90": queda90,

            "rsi": rsi,

            "score": score,

            "status": status,

            "texto_media": interpretar_media(preco, media200),

            "texto_queda": interpretar_queda(queda90),

            "texto_rsi": interpretar_rsi(rsi),

        }

    except Exception as e:
        error(f"Erro no cálculo dos indicadores de {ticker}: {e}", exc_info=True)
        return None