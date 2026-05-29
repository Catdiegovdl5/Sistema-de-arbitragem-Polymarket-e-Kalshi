import requests
from difflib import SequenceMatcher

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
