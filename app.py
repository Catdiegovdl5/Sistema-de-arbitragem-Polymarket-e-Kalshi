import time
from flask import Flask, render_template_string
import requests
from difflib import SequenceMatcher

app = Flask(__name__)

# ==========================================
# 1. CAPTURA DE DADOS REAIS VIA API
# ==========================================

def buscar_dados_polymarket():
    """
    Acessa a API pública Gamma da Polymarket para buscar preços ativos.
    """
    url_publica = "https://gamma-api.polymarket.com/v1/markets?limit=10&closed=false"
    try:
        resposta = requests.get(url_publica, timeout=5)
        if resposta.status_code == 200:
            dados_brutos = resposta.json()
            mercados_formatados = []

            for mercado in dados_brutos:
                if "outcomePrices" in mercado and len(mercado["outcomePrices"]) >= 2:
                    prices = mercado["outcomePrices"]
                    mercados_formatados.append({
                        "id_mercado": f"POLY-{mercado['id']}",
                        "titulo": mercado["question"],
                        "preco_sim": round(float(prices[0]), 2),
                        "preco_nao": round(float(prices[1]), 2),
                        "link": f"https://polymarket.com/event/{mercado.get('slug', '')}"
                    })
            return mercados_formatados
    except Exception as erro:
        print(f"[-] Erro na conexão com Polymarket: {erro}")

    # Fallback de segurança para testes locais offline
    return [{
        "id_mercado": "POLY-EUA-2026",
        "titulo": "Will Donald Trump win the 2026 Presidential Straw Poll?",
        "preco_sim": 0.53, "preco_nao": 0.47,
        "link": "https://polymarket.com"
    }]

def buscar_dados_kalshi():
    """
    Acessa a API pública de mercados da Kalshi para ler os preços vigentes.
    """
    url_publica = "https://blueprint-api.kalshi.com/trade-api/v2/markets?limit=10&status=open"
    try:
        resposta = requests.get(url_publica, timeout=5)
        if resposta.status_code == 200:
            dados_brutos = resposta.json().get("markets", [])
            mercados_formatados = []

            for mercado in dados_brutos:
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
        "titulo": "US Presidential Straw Poll 2026 - Trump Winner",
        "preco_sim": 0.55, "preco_nao": 0.43,
        "link": "https://kalshi.com"
    }]

# ==========================================
# 2. MOTOR DE CORRESPONDÊNCIA DINÂMICA
# ==========================================

def calcular_similaridade(texto1, texto2):
    """
    Calcula a proximidade textual entre duas strings.
    Converte para minúsculas para evitar falhas com letras maiúsculas.
    """
    return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()

# ==========================================
# 3. MOTOR LÓGICO DE ARBITRAGEM
# ==========================================

def processar_arbitragem():
    """
    Cruza as listas de dados dinamicamente usando a inteligência de proximidade textual.
    """
    dados_poly = buscar_dados_polymarket()
    dados_kalshi = buscar_dados_kalshi()
    sinais_encontrados = []

    # Define a margem mínima de similaridade aceitável (50% de compatibilidade)
    CORTE_SIMILARIDADE = 0.50

    for mercado_poly in dados_poly:
        melhor_match = None
        maior_score = 0.0

        # Varre todos os mercados da Kalshi procurando o correspondente ideal
        for mercado_kalshi in dados_kalshi:
            score = calcular_similaridade(mercado_poly["titulo"], mercado_kalshi["titulo"])

            if score > maior_score and score >= CORTE_SIMILARIDADE:
                maior_score = score
                melhor_match = mercado_kalshi

        # Se encontrar uma linha correspondente confiável, calcula a arbitragem
        if melhor_match:
            # Cenário A: Comprar SIM na Polymarket e NÃO na Kalshi
            custo_a = mercado_poly["preco_sim"] + melhor_match["preco_nao"]

            if custo_a < 1.00 and custo_a > 0.1:
                lucro = 1.00 - custo_a
                sinais_encontrados.append({
                    "evento_poly": mercado_poly["titulo"],
                    "evento_kalshi": melhor_match["titulo"],
                    "compra_sim": f"Polymarket (${mercado_poly['preco_sim']})",
                    "compra_nao": f"Kalshi (${melhor_match['preco_nao']})",
                    "custo": round(custo_a, 2),
                    "lucro_pct": round((lucro / custo_a) * 100, 2),
                    "link_poly": mercado_poly["link"],
                    "link_kalshi": melhor_match["link"],
                    "confianca": round(maior_score * 100, 1)
                })

            # Cenário B: Comprar NÃO na Polymarket e SIM na Kalshi
            custo_b = mercado_poly["preco_nao"] + melhor_match["preco_sim"]

            if custo_b < 1.00 and custo_b > 0.1:
                lucro = 1.00 - custo_b
                sinais_encontrados.append({
                    "evento_poly": mercado_poly["titulo"],
                    "evento_kalshi": melhor_match["titulo"],
                    "compra_sim": f"Kalshi (${melhor_match['preco_sim']})",
                    "compra_nao": f"Polymarket (${mercado_poly['preco_nao']})",
                    "custo": round(custo_b, 2),
                    "lucro_pct": round((lucro / custo_b) * 100, 2),
                    "link_poly": mercado_poly["link"],
                    "link_kalshi": melhor_match["link"],
                    "confianca": round(maior_score * 100, 1)
                })

    return sinais_encontrados

# ==========================================
# 4. INTERFACE DE USUÁRIO (DASHBOARD ENGINE)
# ==========================================

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel de Arbitragem Inteligente</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { background-color: #1a1f3c; color: #ffffff; font-family: sans-serif; }
        .card { background-color: #27293d; border: none; border-radius: 8px; margin-top: 40px; }
        .table { color: #ffffff; }
        .badge-lucro { background-color: #00f2c4; color: #1d8cf8; font-weight: bold; }
        .badge-confianca { background-color: #2575fc; color: white; }
        .btn-action { background: linear-gradient(to bottom left, #e14eca, #ba54f5); border: none; color: white; }
        .small-text { font-size: 0.85rem; color: #a9a9b9; }
    </style>
    <script>
        setInterval(function(){ window.location.reload(); }, 5000);
    </script>
</head>
<body>
    <div class="container-fluid px-5">
        <div class="card p-4 shadow">
            <h2 class="mb-2">🚨 Monitor de Arbitragem com Pareamento Dinâmico</h2>
            <p class="text-muted mb-4">Análise automática por Proximidade Textual ativa (Atualizando a cada 5s)...</p>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Mercados Cruzados (Poly vs Kalshi)</th>
                            <th>Confiança Match</th>
                            <th>Comprar SIM</th>
                            <th>Comprar NÃO</th>
                            <th>Custo</th>
                            <th>ROI Estimado</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for sinal in sinais %}
                        <tr>
                            <td>
                                <div><span class="badge badge-info font-weight-light">Poly</span> {{ sinal.evento_poly }}</div>
                                <div class="mt-1"><span class="badge badge-warning text-dark font-weight-light">Kalshi</span> <span class="small-text">{{ sinal.evento_kalshi }}</span></div>
                            </td>
                            <td><span class="badge badge-confianca p-2">{{ sinal.confianca }}%</span></td>
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
                            <td colspan="7" class="text-center text-muted">Aguardando gatilhos... O robô está varrendo e cruzando os tópicos das APIs abertas.</td>
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
