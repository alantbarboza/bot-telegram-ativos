from logging import error
import yfinance as yf

def calcular_rsi(close, periodo=14):
    delta = close.diff()

    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)

    media_ganho = ganho.rolling(periodo).mean()
    media_perda = perda.rolling(periodo).mean()

    rs = media_ganho / media_perda

    return 100 - (100 / (1 + rs))


def score_media(preco, media):
    percentual = ((media - preco) / media) * 100
    return max(0, min(percentual * 10, 100))


def score_queda(queda):
    return max(0, min(queda * 5, 100))


def score_rsi(rsi):
    if rsi <= 30:
        return 100

    if rsi >= 70:
        return 0

    return (70 - rsi) / 40 * 100


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
            return None
            
    except Exception as e:
        error(f"Erro ao analisar {ticker}: {e}")
        return None

    close = df["Close"].iloc[:, 0]
    high = df["High"].iloc[:, 0]

    preco = float(close.iloc[-1])

    media30 = float(close.tail(30).mean())
    media200 = float(close.tail(200).mean())

    maxima90 = float(high.tail(90).max())
    queda90 = (maxima90 - preco) / maxima90 * 100

    rsi = float(calcular_rsi(close).iloc[-1])

    score = round(
        score_media(preco, media200) * 0.40 +
        score_queda(queda90) * 0.30 +
        score_rsi(rsi) * 0.20 +
        score_media(preco, media30) * 0.10
    )

    if score >= 80:
        status = "🟢 Excelente oportunidade"

    elif score >= 60:
        status = "🟢 Boa oportunidade"

    elif score >= 40:
        status = "🟡 Oportunidade moderada"

    elif score >= 20:
        status = "🟠 Pouca oportunidade"

    else:
        status = "🔴 Aguarde uma correção"

    return {
        "ticker": ticker.replace(".SA", ""),
        "preco": preco,
        "media30": media30,
        "media200": media200,
        "queda90": queda90,
        "rsi": rsi,
        "score": score,
        "status": status,
    }