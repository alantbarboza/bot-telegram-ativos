# Bot Telegram de Análise de Ativos

## Sobre o projeto

O sistema consulta dados históricos do Yahoo Finance, calcula médias móveis, compara o preço atual com essas referências e envia relatórios diretamente pelo Telegram.

O projeto fornece um resumo do preço atual, da máxima e mínima do dia, das médias móveis de 30 e 200 pregões e informa se o ativo está sendo negociado abaixo ou acima dessas médias, facilitando o acompanhamento dos ativos.

Este projeto foi desenvolvido com foco em automação, integração com APIs, programação assíncrona, análise de dados financeiros e organização de aplicações Python.

---

## Funcionalidades

* Geração automática de relatórios dos ativos configurados.
* Geração manual de relatórios por meio de comandos do Telegram.
* Cálculo automático das médias móveis de 30 e 200 pregões.
* Exibição do preço máximo e mínimo do pregão atual.
* Comparação entre o preço atual e as médias móveis. 
* Envio automático de relatórios a cada hora.
* Controle para impedir execuções simultâneas.
* Controle de permissões para grupos do Telegram.
* Gerenciamento dos usuários autorizados, horários de execução e ativos monitorados via arquivo de configuração.
* Consulta automática de dados históricos utilizando Yahoo Finance.
* Relatórios em linguagem simples para facilitar a interpretação dos indicadores.

---

## Ativos monitorados

Os ativos analisados são definidos individualmente para cada usuário no arquivo `usuarios.json`.

Cada usuário pode possuir uma lista própria de ativos, permitindo que diferentes usuários recebam relatórios personalizados.

---

## Como funciona a análise

1. A cada hora cheia, o bot verifica se existe uma execução agendada para cada usuário.
2. Caso exista, carrega os ativos configurados para aquele usuário.
3. Obtém os dados históricos utilizando a API do Yahoo Finance.
4. Calcula automaticamente:
   * Preço atual
   * Preço máximo do pregão atual
   * Preço mínimo do pregão atual
   * Média móvel dos últimos 30 pregões
   * Média móvel dos últimos 200 pregões (ou o histórico disponível, quando inferior)
   * Diferença percentual entre o preço atual e cada média móvel
5. Compara o preço atual com a média móvel de 200 pregões e informa se ele está abaixo, próximo ou acima da média histórica.
6. Envia o relatório diretamente pelo Telegram.

**Observação:** O sistema impede execuções simultâneas. Caso um relatório manual (`/relatorio`) esteja em andamento, a execução automática será ignorada, e vice-versa.

---

## Como é feita a comparação

O objetivo do relatório é responder de forma simples à pergunta:

> O preço atual está abaixo da média?

Para isso, o sistema calcula duas médias móveis:

- Média dos últimos 30 pregões;
- Média dos últimos 200 pregões.

Em seguida calcula a diferença percentual entre o preço atual e cada média:
```text
Diferença (%) = ((Preço Atual - Média) / Média) × 100
```

Interpretação:

| Resultado | Significado |
|-----------:|------------|
| Negativo | Preço abaixo da média |
| Zero | Preço igual à média |
| Positivo | Preço acima da média |

A média de 200 pregões é utilizada como principal referência para indicar se o ativo está negociando abaixo ou acima do seu preço médio histórico recente.

Importante: Estar abaixo da média não representa, por si só, uma recomendação de compra. A comparação serve apenas como uma referência para indicar se o preço atual está negociando abaixo ou acima das médias móveis analisadas.

---

## Comandos disponíveis

### Relatórios

* `/relatorio` - Gera o relatório imediatamente.
* `/proxima_execucao` - Exibe a próxima execução automática.
* `/online` - Mostra o tempo que o bot está online.

### Utilidades

* `/comandos` - Lista todos os comandos disponíveis.
* `/meu_id` - Exibe o ID do usuário.
* `/limpar` - Remove as mensagens armazenadas pelo bot.

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/alantbarboza/bot-telegram-ativos.git
cd bot-telegram-ativos
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
API_KEY=sua_api_key
PORT=10000
WEBHOOK_URL=https://seu-servico.onrender.com
```

Onde:

* `API_KEY`: token do Bot do Telegram.
* `PORT`: porta utilizada pelo servidor HTTP.
* `WEBHOOK_URL`: URL pública onde o bot está hospedado (Render, Railway, etc.).

### 4. Configure os usuários

No arquivo `usuarios.json`, informe os usuários autorizados, o horário da próxima execução automática e os ativos que cada usuário deseja monitorar.

Exemplo:

```json
{
    "123456789": {
        "nome": "Alan",
        "proxima_execucao": "2026-07-24T20:00:00-03:00",
        "ativos": [
            "BEST11.SA",
            "NDIV11.SA",
            "WRLD11.SA"
        ]
    }
}
```

### 5. Execute o projeto

```bash
python main.py
```

---

## Tecnologias utilizadas

* Python
* Aiogram (Telegram Bot Framework)
* aiohttp (Servidor Web / Webhook)
* AsyncIO (Programação assíncrona)
* Yahoo Finance (Coleta de dados financeiros)
* Pandas (Manipulação de dados)
* Telegram Bot API

---

## Estrutura do projeto

```text
bot-telegram-ativos/

├── bot/
├── relatorio/
├── agendamento/
├── utils/
├── main.py
└── requirements.txt
```