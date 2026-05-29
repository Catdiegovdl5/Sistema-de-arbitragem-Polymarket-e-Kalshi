import time
from flask import Flask, render_template_string

app = Flask(__name__)

# ==========================================
# SIMULAÇÃO DE DADOS (ESTRUTURA DE API REAL)
# ==========================================

def buscar_dados_polymarket():
    """
    Simula o retorno de carga útil JSON da API da Polymarket V2.
    Em produção, substitui por requests.get("https://clob.polymarket.com/v1/...")
    """
    return [
        {
            "id_mercado": "POLY-EUA-2026",
            "titulo": "Will Donald Trump win the 2026 Presidential Straw Poll?",
            "preco_sim": 0.53,
            "preco_nao": 0.47,
            "link": "https://polymarket.com/event/straw-poll-2026"
        },
        {
            "id_mercado": "POLY-FED-JUROS",
            "titulo": "Will the Fed cut interest rates in June?",
            "preco_sim": 0.62,
            "preco_nao": 0.38,
            "link": "https://polymarket.com/event/fed-interest-rates"
        }
    ]

def buscar_dados_kalshi():
    """
    Simula o retorno de carga útil JSON da API da Kalshi v2.
    Em produção, substitui por requests.get("https://external-api.kalshi.com/trade-api/v2/...")
    """
    return [
        {
            "id_mercado": "KALSHI-PRES-POLL",
            "titulo": "US Presidential Straw Poll 2026 - Trump Winner",
            "preco_sim": 0.55,
            "preco_nao": 0.43,  # Spread detectável aqui: 0.53 + 0.43 = 0.96 (Lucro)
            "link": "https://kalshi.com/markets/pres-poll"
        },
        {
            "id_mercado": "KALSHI-FED-JUNE",
            "titulo": "Fed Interest Rate Cut in June Meeting",
            "preco_sim": 0.61,
            "preco_nao": 0.39,
            "link": "https://kalshi.com/markets/fed-june"
        }
    ]

# ==========================================
# DICIONÁRIO DE PAREAMENTO (MATCHING MAPPING)
# ==========================================

# Resolve o gargalo de nomes diferentes para o mesmo evento nas duas plataformas
DICIONARIO_MAPEAMENTO = {
    "POLY-EUA-2026": "KALSHI-PRES-POLL",
    "POLY-FED-JUROS": "KALSHI-FED-JUNE"
}

# ==========================================
# MOTOR LOGICO DE ARBITRAGEM
# ==========================================

def processar_arbitragem():
    """
    Cruza as listas de dados (Arrays), calcula a distorção matemática
    e ativa o gatilho (Trigger) sempre que o custo combinado for menor que $1.00.
    """
    dados_poly = buscar_dados_polymarket()
    dados_kalshi = buscar_dados_kalshi()

    # Indexação O(1) para busca rápida de performance de hardware
    mapa_kalshi = {m["id_mercado"]: m for m in dados_kalshi}
    sinais_encontrados = []

    for mercado_poly in dados_poly:
        id_poly = mercado_poly["id_mercado"]
        id_kalshi_correspondente = DICIONARIO_MAPEAMENTO.get(id_poly)

        if id_kalshi_correspondente and id_kalshi_correspondente in mapa_kalshi:
            mercado_kalshi = mapa_kalshi[id_kalshi_correspondente]

            # Cenário A: Comprar SIM na Polymarket e NÃO na Kalshi
            custo_a = mercado_poly["preco_sim"] + mercado_kalshi["preco_nao"]
            if custo_a < 1.00:
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

            # Cenário B: Comprar NÃO na Polymarket e SIM na Kalshi
            custo_b = mercado_poly["preco_nao"] + mercado_kalshi["preco_sim"]
            if custo_b < 1.00:
                lucro = 1.00 - custo_b
                sinais_encontrados.append({
                    "evento": mercado_poly["titulo"],
                    "compra_sim": f"Kalshi (${mercado_kalshi['preco_sim']})",
                    "compra_nao": f"Polymarket (${mercado_poly['preco_nao']})",
                    "custo": round(custo_b, 2),
                    "lucro_pct": round((lucro / custo_b) * 100, 2),
                    "link_poly": mercado_poly["link"],
                    "link_kalshi": mercado_kalshi["link"]
                })

    return sinais_encontrados

# ==========================================
# ROTAS INTERNAS DO DASHBOARD FLASK
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
</head>
<body>
    <div class="container">
        <div class="card p-4 shadow">
            <h2 class="mb-4">🚨 Sinais de Arbitragem de Alta Performance</h2>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Evento Monitorado</th>
                            <th>Onde Comprar SIM</th>
                            <th>Onde Comprar NÃO</th>
                            <th>Custo Operacional</th>
                            <th>Retorno Estimado (ROI)</th>
                            <th>Links de Execução</th>
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
                            <td colspan="6" class="text-center text-muted">Aguardando gatilhos de spread lucrativo...</td>
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
    # Roda localmente com recarga automática ativa para desenvolvimento
    app.run(debug=True, port=5000)
