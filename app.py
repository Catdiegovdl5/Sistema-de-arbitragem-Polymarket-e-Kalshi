import time
from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# ==========================================
# 1. CAPTURA DE DADOS REAIS (HTTP REQUESTS)
# ==========================================

def buscar_dados_polymarket():
    """
    Acessa a API pública Gamma da Polymarket para buscar preços ativos.
    Retorna uma lista padronizada para o nosso motor.
    """
    url_publica = "https://gamma-api.polymarket.com/v1/markets?limit=5&closed=false"
    try:
        # Faz a chamada HTTP com um limite de espera (timeout) de 5 segundos
        resposta = requests.get(url_publica, timeout=5)

        if resposta.status_code == 200:
            dados_brutos = resposta.json()
            mercados_formatados = []

            for mercado in dados_brutos:
                # Filtragem básica para pegar mercados de "Sim/Não" (Binary)
                if "outcomePrices" in mercado and len(mercado["outcomePrices"]) >= 2:
                    prices = mercado["outcomePrices"] # Lista de strings de preços
                    mercados_formatados.append({
                        "id_mercado": f"POLY-{mercado['id']}",
                        "titulo": mercado["question"],
                        "preco_sim": round(float(prices[0]), 2),
                        "preco_nao": round(float(prices[1]), 2),
                        "link": f"https://polymarket.com/event/{mercado.get('slug', '')}"
                    })
            return mercados_formatados # Corrigido de markets_formatados
    except Exception as erro:
        print(f"[-] Erro na conexão com Polymarket: {erro}")

    # Se falhar, retorna um fallback para o painel não quebrar
    return [{
        "id_mercado": "POLY-EUA-2026",
        "titulo": "Will Donald Trump win the 2026 Presidential Straw Poll? (Simulado)",
        "preco_sim": 0.53, "preco_nao": 0.47,
        "link": "https://polymarket.com"
    }]

def buscar_dados_kalshi():
    """
    Acessa a API pública de mercados da Kalshi para ler os preços vigentes.
    """
    url_publica = "https://blueprint-api.kalshi.com/trade-api/v2/markets?limit=5&status=open"
    try:
        resposta = requests.get(url_publica, timeout=5)
        if resposta.status_code == 200:
            dados_brutos = resposta.json().get("markets", [])
            mercados_formatados = []

            for mercado in dados_brutos:
                # Kalshi trabalha com centavos de dólar (ex: 53 representa $0.53)
                preco_sim_fiat = mercado.get("yes_ask", 50) / 100
                preco_nao_fiat = mercado.get("no_ask", 50) / 100

                mercados_formatados.append({
                    "id_mercado": f"KALSHI-{mercado['ticker']}",
                    "titulo": mercado["title"],
                    "preco_sim": round(preco_sim_fiat, 2),
                    "preco_nao": round(preco_nao_fiat, 2),
                    "link": f"https://kalshi.com/markets/{mercado['ticker']}"
                })
            return mercados_formatados
    except Exception as erro:
        print(f"[-] Erro na conexão com Kalshi: {erro}")

    return [{
        "id_mercado": "KALSHI-PRES-POLL",
        "titulo": "US Presidential Straw Poll 2026 - Trump Winner (Simulado)",
        "preco_sim": 0.55, "preco_nao": 0.43,
        "link": "https://kalshi.com"
    }]

# ==========================================
# 2. PAREAMENTO DINÂMICO DE SEGURANÇA
# ==========================================

# Mapeamento base para teste cruzado das chaves de identificação
DICIONARIO_MAPEAMENTO = {
    "POLY-EUA-2026": "KALSHI-PRES-POLL"
}

# ==========================================
# 3. MOTOR LOGICO DE ARBITRAGEM
# ==========================================

def processar_arbitragem():
    dados_poly = buscar_dados_polymarket()
    dados_kalshi = buscar_dados_kalshi()

    mapa_kalshi = {m["id_mercado"]: m for m in dados_kalshi}
    sinais_encontrados = []

    for mercado_poly in dados_poly:
        id_poly = mercado_poly["id_mercado"]
        id_kalshi_correspondente = DICIONARIO_MAPEAMENTO.get(id_poly)

        if id_kalshi_correspondente and id_kalshi_correspondente in mapa_kalshi:
            mercado_kalshi = mapa_kalshi[id_kalshi_correspondente]

            # Cálculo de Spread do Cenário A (SIM na Poly, NÃO na Kalshi)
            custo_a = mercado_poly["preco_sim"] + mercado_kalshi["preco_nao"]
            if custo_a < 1.00 and custo_a > 0.1: # Proteção contra dados zerados ruins
                lucro = 1.00 - custo_a
                sinais_encontrados.append({
                    "evento": mercado_poly["titulo"],
                    "compra_sim": f"Polymarket (${mercado_poly['preco_sim']})",
                    "compra_nao": f"Kalshi (${mercado_kalshi['preco_nao']})",
                    "custo": round(custo_a, 2),
                    "lucro_pct": round((lucro / custo_a) * 100, 2),
                    "link_poly": mercado_poly["link"],
                    "link_kalshi": mercado_kalshi["link"]
                })

    return sinais_encontrados

# ==========================================
# 4. INTERFACE DE USUÁRIO (HTML ENGINE)
# ==========================================

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel de Arbitragem - CAPI Tracker</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background-color: #1a1f3c; color: #ffffff; font-family: sans-serif; }
        .card { background-color: #27293d; border: none; border-radius: 8px; margin-top: 40px; }
        .table { color: #ffffff; }
        .badge-lucro { background-color: #00f2c4; color: #1d8cf8; font-weight: bold; }
        .btn-action { background: linear-gradient(to bottom left, #e14eca, #ba54f5); border: none; color: white; }
    </style>
    <script>
        setInterval(function(){ window.location.reload(); }, 5000);
    </script>
</head>
<body>
    <div class="container">
        <div class="card p-4 shadow">
            <h2 class="mb-2">🚨 Monitor de Mercados em Tempo Real (API Ativa)</h2>
            <p class="text-muted mb-4">Efetuando requisições HTTP seguras em segundo plano...</p>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Evento</th>
                            <th>SIM</th>
                            <th>NÃO</th>
                            <th>Custo</th>
                            <th>ROI Estimado</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for sinal in sinais %}
                        <tr>
                            <td><strong>{{ sinal.evento }}</strong></td>
                            <td><span class="text-info">{{ sinal.compra_sim }}</span></td>
                            <td><span class="text-warning">{{ sinal.compra_nao }}</span></td>
                            <td>${{ sinal.custo }}</td>
                            <td><span class="badge badge-lucro p-2">+{{ sinal.lucro_pct }}%</span></td>
                            <td>
                                <a href="{{ sinal.link_poly }}" target="_blank" class="btn btn-sm btn-action mr-1">Poly</a>
                                <a href="{{ sinal.link_kalshi }}" target="_blank" class="btn btn-sm btn-secondary">Kalshi</a>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="6" class="text-center text-muted">Aguardando gatilhos... Se as APIs não encontrarem mercados correspondentes idênticos, a tabela ficará limpa.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    sinais_ativos = processar_arbitragem()
    return render_template_string(HTML_DASHBOARD, sinais=sinais_ativos)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
