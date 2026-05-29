import time
from flask import Flask, render_template_string
import requests
from difflib import SequenceMatcher

app = Flask(__name__)

# ==========================================
# 1. NORMALIZADOR E LIMPEZA DE TEXTO
# ==========================================

def limpar_titulo(texto):
    """
    Remove pontuações e palavras acessórias comuns para isolar os
    termos chave do mercado, otimizando a taxa de acerto do algoritmo.
    """
    termo_minusculo = texto.lower()
    palavras_ruido = ["will", "the", "win", "is", "a", "in", "on", "at", "to", "be", "by", "of", "for", "meeting", "presidential", "who"]
    
    for caractere in ["?", "!", ".", ",", "-", '"', "'"]:
        termo_minusculo = termo_minusculo.replace(caractere, " ")
        
    palavras_filtradas = [palavra for palavra in termo_minusculo.split() if palavra not in palavras_ruido]
    return " ".join(palavras_filtradas)

# ==========================================
# 2. CAPTURA EM LARGA ESCALA (LIMIT=100)
# ==========================================

def buscar_dados_polymarket():
    url_publica = "https://gamma-api.polymarket.com/v1/markets?limit=100&closed=false&active=true"
    try:
        resposta = requests.get(url_publica, timeout=6)
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
        print(f"[-] Erro de Rate Limit Polymarket: {erro}")
    return []

def buscar_dados_kalshi():
    url_publica = "https://external-api.kalshi.com/trade-api/v2/markets?limit=100&status=open"
    try:
        resposta = requests.get(url_publica, timeout=6)
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
        print(f"[-] Erro de Rate Limit Kalshi: {erro}")
    return []

# ==========================================
# 3. MOTOR DE ARBITRAGEM (MODO RADAR)
# ==========================================

def calcular_similaridade(texto1, texto2):
    t1_limpo = limpar_titulo(texto1)
    t2_limpo = limpar_titulo(texto2)
    return SequenceMatcher(None, t1_limpo, t2_limpo).ratio()

def processar_arbitragem():
    dados_poly = buscar_dados_polymarket()
    dados_kalshi = buscar_dados_kalshi()
    sinais_encontrados = []
    
    # Sensibilidade reduzida para encontrar mais correspondências para o dashboard
    CORTE_SIMILARIDADE = 0.45 
    
    for mercado_poly in dados_poly:
        melhor_match = None
        maior_score = 0.0
        
        for mercado_kalshi in dados_kalshi:
            score = calcular_similaridade(mercado_poly["titulo"], mercado_kalshi["titulo"])
            if score > maior_score and score >= CORTE_SIMILARIDADE:
                maior_score = score
                melhor_match = mercado_kalshi
                
        if melhor_match:
            # Calcula os dois cenários e escolhe sempre o mais barato para exibir
            custo_a = mercado_poly["preco_sim"] + melhor_match["preco_nao"]
            custo_b = mercado_poly["preco_nao"] + melhor_match["preco_sim"]
            
            if custo_a < custo_b:
                melhor_custo = custo_a
                compra_sim = f"Poly (${mercado_poly['preco_sim']})"
                compra_nao = f"Kalshi (${melhor_match['preco_nao']})"
            else:
                melhor_custo = custo_b
                compra_sim = f"Kalshi (${melhor_match['preco_sim']})"
                compra_nao = f"Poly (${mercado_poly['preco_nao']})"
            
            # Filtro de sanidade: ignora dados corrompidos abaixo de 15 cêntimos e acima de $1.20
            if 0.15 < melhor_custo < 1.20:
                lucro_pct = round(((1.00 - melhor_custo) / melhor_custo) * 100, 2)
                
                sinais_encontrados.append({
                    "evento_poly": mercado_poly["titulo"],
                    "evento_kalshi": melhor_match["titulo"],
                    "compra_sim": compra_sim,
                    "compra_nao": compra_nao,
                    "custo": round(melhor_custo, 2),
                    "lucro_pct": lucro_pct,
                    "is_profitable": melhor_custo < 1.00, # Flag booleana para o UI
                    "link_poly": mercado_poly["link"],
                    "link_kalshi": melhor_match["link"],
                    "confianca": round(maior_score * 100, 1)
                })
                
    # Ordena a lista para mostrar os cenários mais próximos de dar lucro no topo
    sinais_encontrados = sorted(sinais_encontrados, key=lambda x: x['custo'])
    # Retorna apenas os 10 melhores resultados para não poluir o ecrã
    return sinais_encontrados[:10]

# ==========================================
# 4. DASHBOARD ENGINE (CREATIVE TIM UI)
# ==========================================

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>CAPI Arbitrage - Black Dashboard</title>
    <link href="https://fonts.googleapis.com/css?family=Poppins:200,300,400,600,700,800" rel="stylesheet" />
    <link href="https://use.fontawesome.com/releases/v5.0.6/css/all.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #1e1e2f; color: #ffffff; font-family: 'Poppins', sans-serif; margin: 0; overflow-x: hidden; }
        .sidebar { background: #1e1e2f; width: 260px; position: fixed; top: 0; bottom: 0; left: 0; z-index: 10; border-right: 1px solid #2b2b40; }
        .sidebar .logo { padding: 18px 20px; border-bottom: 1px solid #2b2b40; font-weight: 400; font-size: 1.1rem; color: #ffffff; text-align: left; text-transform: uppercase; letter-spacing: 1px; }
        .sidebar .nav { margin-top: 20px; padding: 0; list-style: none; }
        .sidebar .nav li { margin: 10px 15px; }
        .sidebar .nav li a { color: #ffffff; text-decoration: none; padding: 12px 15px; border-radius: 5px; display: block; background: linear-gradient(0deg, #ba54f5 0%, #e14eca 100%); box-shadow: 0 4px 20px 0 rgba(0,0,0,.14), 0 7px 10px -5px rgba(225,78,202,.4); }
        .sidebar .nav li a i { font-size: 1.2rem; margin-right: 12px; float: left; text-align: center; }
        .main-panel { position: relative; float: right; width: calc(100% - 260px); background-color: #1e1e2f; min-height: 100vh; padding: 20px 30px; }
        .card { background: #27293d; border: 0; border-radius: 0.2857rem; box-shadow: 0 1px 20px 0px rgba(0,0,0,.1); margin-bottom: 30px; }
        .card-header { background: transparent; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 15px 20px; }
        .card-title { font-weight: 200; color: #ffffff; font-size: 1.5rem; margin: 0; }
        .table { color: rgba(255, 255, 255, 0.7); margin-bottom: 0; }
        .table thead th { border-bottom: 1px solid rgba(255,255,255,0.1) !important; border-top: none; font-weight: 400; color: rgba(255,255,255,0.5); font-size: 0.8rem; text-transform: uppercase; }
        .table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.05); transition: 0.2s; }
        .table tbody tr:hover { background-color: rgba(255,255,255,0.03); }
        .table td { border-bottom: none; vertical-align: middle; padding: 16px 12px; }
        .badge-lucro { background-color: #00f2c3; color: #1e1e2f; font-weight: 600; padding: 6px 12px; border-radius: 4px; font-size: 0.9rem; }
        .badge-monitor { background-color: #ff8d72; color: #1e1e2f; font-weight: 600; padding: 6px 12px; border-radius: 4px; font-size: 0.8rem; }
        .badge-confianca { background-color: #1d8cf8; color: #fff; padding: 5px 10px; border-radius: 4px; font-weight: 400; }
        .badge-plataforma { font-size: 0.65rem; padding: 4px 6px; margin-right: 8px; font-weight: 600; border-radius: 3px; }
        .btn-poly { background: #1d8cf8; color: #fff; text-decoration: none; padding: 7px 15px; border-radius: 4px; border: none; font-size: 0.8rem; font-weight: 500; transition: 0.3s; }
        .btn-kalshi { background: #344675; color: #fff; text-decoration: none; padding: 7px 15px; border-radius: 4px; border: none; font-size: 0.8rem; font-weight: 500; transition: 0.3s; }
        .btn-poly:hover, .btn-kalshi:hover { opacity: 0.8; color: white; transform: translateY(-1px); }
        .text-info-custom { color: #1d8cf8 !important; font-weight: 600; }
        .text-warning-custom { color: #ff8d72 !important; font-weight: 600; }
        .small-title { font-size: 0.85rem; color: #9a9a9a; font-weight: 300; }
    </style>
    <script>
        setInterval(function(){ window.location.reload(); }, 5000);
    </script>
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <i class="fas fa-robot text-info mr-2"></i> CAPI Tracker
        </div>
        <ul class="nav">
            <li>
                <a href="#">
                    <i class="fas fa-chart-pie"></i>
                    <p class="m-0">Sinais de Arbitragem</p>
                </a>
            </li>
        </ul>
    </div>
    
    <div class="main-panel">
        <nav class="navbar navbar-expand-lg navbar-dark bg-transparent mb-4">
            <div class="container-fluid p-0">
                <span class="navbar-brand font-weight-bold" style="font-size: 1.4rem;">Monitoramento Estratégico (Radar)</span>
            </div>
        </nav>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h4 class="card-title"><i class="fas fa-satellite-dish text-info-custom me-2"></i> Top 10 Spreads Ativos</h4>
                        <span class="badge" style="background: rgba(255,255,255,0.1); color: #fff; font-weight: 400;"><i class="fas fa-sync-alt fa-spin me-2 text-info-custom"></i>Auto-Refresh: 5s</span>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Cruzamento Automático (NLP)</th>
                                        <th class="text-center">Confiança</th>
                                        <th>Compra SIM</th>
                                        <th>Compra NÃO</th>
                                        <th class="text-center">Custo Base</th>
                                        <th class="text-center">Status (ROI)</th>
                                        <th class="text-center">Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for sinal in sinais %}
                                    <tr>
                                        <td>
                                            <div class="mb-2"><span class="badge badge-plataforma bg-info text-dark">POLY</span> <span class="text-white">{{ sinal.evento_poly }}</span></div>
                                            <div><span class="badge badge-plataforma bg-warning text-dark">KAL</span> <span class="small-title">{{ sinal.evento_kalshi }}</span></div>
                                        </td>
                                        <td class="text-center"><span class="badge-confianca">{{ sinal.confianca }}%</span></td>
                                        <td class="text-info-custom">{{ sinal.compra_sim }}</td>
                                        <td class="text-warning-custom">{{ sinal.compra_nao }}</td>
                                        <td class="text-center" style="color: #fff; font-weight: 500; font-size: 1.1rem;">${{ sinal.custo }}</td>
                                        
                                        <!-- Lógica de Renderização de Status -->
                                        <td class="text-center">
                                            {% if sinal.is_profitable %}
                                                <span class="badge-lucro">+{{ sinal.lucro_pct }}% (LUCRO)</span>
                                            {% else %}
                                                <span class="badge-monitor">{{ sinal.lucro_pct }}% (VIGIANDO)</span>
                                            {% endif %}
                                        </td>
                                        
                                        <td class="text-center">
                                            <a href="{{ sinal.link_poly }}" target="_blank" class="btn-poly me-1">Poly</a>
                                            <a href="{{ sinal.link_kalshi }}" target="_blank" class="btn-kalshi">Kalshi</a>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr>
                                        <td colspan="7" class="text-center py-5" style="color: #9a9a9a;">
                                            <i class="fas fa-circle-notch fa-spin fa-3x mb-3 text-info-custom"></i>
                                            <h5 class="font-weight-light">Extraindo Livro de Ofertas...</h5>
                                            <p class="small-title m-0">Iniciando o mapeamento das plataformas de previsão.</p>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
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