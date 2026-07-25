# Bot Telegram de Análise de Ativos

## Sobre o projeto

Bot desenvolvido em Python para realizar análises automáticas de ativos financeiros utilizando dados do Yahoo Finance, calculando indicadores técnicos e enviando relatórios diretamente pelo Telegram.

O objetivo do projeto é acompanhar ativos de forma automatizada, facilitando a identificação de oportunidades de compra sem a necessidade de consultar gráficos manualmente.

Este projeto foi desenvolvido com foco em automação, integração com APIs, programação assíncrona, análise de dados financeiros e organização de aplicações Python.

---

## Funcionalidades

* Geração automática de relatórios dos ativos configurados.
* Geração manual de relatórios através de comandos do Telegram.
* Cálculo automático dos principais indicadores técnicos.
* Classificação dos ativos por score de oportunidade.
* Envio automático de relatórios a cada hora.
* Controle para impedir execuções simultâneas.
* Controle de permissões para grupos do Telegram.
* Gerenciamento dos usuários autorizados, horários de execução e ativos monitorados via arquivo de configuração.

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
   * Média móvel de 30 dias
   * Média móvel de 200 dias
   * Queda em relação à máxima dos últimos 90 dias
   * RSI (Índice de Força Relativa)
5. Calcula um score de oportunidade baseado nos indicadores.
6. Classifica cada ativo conforme o score obtido.
7. Envia o relatório diretamente pelo Telegram.

**Observação:** O sistema impede execuções simultâneas. Caso um relatório manual (`/relatorio`) esteja em andamento, a execução automática será ignorada, e vice-versa.

---

## Sistema de pontuação

Cada ativo recebe uma pontuação de 0 a 100 considerando:

* Distância da Média Móvel de 200 dias
* Distância da Média Móvel de 30 dias
* Queda em relação à máxima dos últimos 90 dias
* Índice RSI (14 períodos)

Com base na pontuação, o ativo é classificado como:

* 🟢 Excelente oportunidade
* 🟢 Boa oportunidade
* 🟡 Oportunidade moderada
* 🟠 Pouca oportunidade
* 🔴 Aguarde uma correção

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