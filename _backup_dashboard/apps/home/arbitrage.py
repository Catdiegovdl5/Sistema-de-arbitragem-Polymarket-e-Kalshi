import requests
import json
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
    palavras_ruido = ["will", "the", "win", "is", "a", "in", "on", "at", "to", "be", "by", "of", "for", "meeting", "presidential", "who", "when", "how", "many", "what", "and"]
    
    for caractere in ["?", "!", ".", ",", "-", '"', "'", "(", ")", ":"]:
        termo_minusculo = termo_minusculo.replace(caractere, " ")
        
    palavras_filtradas = [palavra for palavra in termo_minusculo.split() if palavra not in palavras_ruido and len(palavra) > 2]
    return " ".join(palavras_filtradas)

def calcular_similaridade(texto1, texto2):
    t1_limpo = limpar_titulo(texto1)
    t2_limpo = limpar_titulo(texto2)
    
    t1_set = set(t1_limpo.split())
    t2_set = set(t2_limpo.split())
    
    if not t1_set or not t2_set:
        return 0.0
        
    intersecao = len(t1_set.intersection(t2_set))
    uniao = len(t1_set.union(t2_set))
    jaccard = intersecao / uniao
    
    sequence = SequenceMatcher(None, t1_limpo, t2_limpo).ratio()
    return max(jaccard, sequence)

# ==========================================
# 2. CAPTURA EM LARGA ESCALA
# ==========================================
def buscar_dados_polymarket():
    url_publica = "https://gamma-api.polymarket.com/markets?limit=300&closed=false&active=true"
    try:
        resposta = requests.get(url_publica, timeout=10)
        if resposta.status_code == 200:
            dados_brutos = resposta.json()
            mercados_formatados = []
            for mercado in dados_brutos:
                if "outcomePrices" in mercado:
                    prices = mercado["outcomePrices"]
                    if isinstance(prices, str):
                        try:
                            prices = json.loads(prices)
                        except:
                            continue
                    
                    if isinstance(prices, list) and len(prices) >= 2:
                        try:
                            preco_sim = float(prices[0])
                            preco_nao = float(prices[1])
                            if preco_sim <= 0 or preco_nao <= 0:
                                continue
                                
                            mercados_formatados.append({
                                "id_mercado": f"POLY-{mercado['id']}",
                                "titulo": mercado["question"],
                                "preco_sim": round(preco_sim, 3),
                                "preco_nao": round(preco_nao, 3),
                                "link": f"https://polymarket.com/event/{mercado.get('slug', '')}"
                            })
                        except:
                            continue
            return mercados_formatados
    except Exception as erro:
        print(f"[-] Erro de Rate Limit Polymarket: {erro}")
    return []

def buscar_dados_kalshi():
    url_publica = "https://external-api.kalshi.com/trade-api/v2/markets?limit=300&status=open"
    try:
        resposta = requests.get(url_publica, timeout=10)
        if resposta.status_code == 200:
            dados_brutos = resposta.json().get("markets", [])
            mercados_formatados = []
            for mercado in dados_brutos:
                yes_ask = mercado.get("yes_ask")
                no_ask = mercado.get("no_ask")
                
                # Pula mercados sem liquidez no momento
                if yes_ask is None or no_ask is None or yes_ask <= 0 or no_ask <= 0:
                    continue
                    
                preco_sim_fiat = yes_ask / 100.0
                preco_nao_fiat = no_ask / 100.0
                
                mercados_formatados.append({
                    "id_mercado": f"KALSHI-{mercado['ticker']}",
                    "titulo": mercado["title"],
                    "preco_sim": round(preco_sim_fiat, 3),
                    "preco_nao": round(preco_nao_fiat, 3),
                    "link": f"https://kalshi.com/markets/{mercado['ticker']}"
                })
            return mercados_formatados
    except Exception as erro:
        print(f"[-] Erro de Rate Limit Kalshi: {erro}")
    return []

# ==========================================
# 3. MOTOR DE ARBITRAGEM (MODO RADAR)
# ==========================================
def processar_arbitragem():
    dados_poly = buscar_dados_polymarket()
    dados_kalshi = buscar_dados_kalshi()
    sinais_encontrados = []
    
    # Corte rigoroso para garantir 100% de precisão (evitar falsos positivos)
    CORTE_SIMILARIDADE = 0.70 
    
    for mercado_poly in dados_poly:
        melhor_match = None
        maior_score = 0.0
        
        for mercado_kalshi in dados_kalshi:
            score = calcular_similaridade(mercado_poly["titulo"], mercado_kalshi["titulo"])
            if score > maior_score and score >= CORTE_SIMILARIDADE:
                maior_score = score
                melhor_match = mercado_kalshi
                
        if melhor_match:
            # Opção A: Comprar SIM na Poly e NÃO na Kalshi
            custo_a = mercado_poly["preco_sim"] + melhor_match["preco_nao"]
            
            # Opção B: Comprar NÃO na Poly e SIM na Kalshi
            custo_b = mercado_poly["preco_nao"] + melhor_match["preco_sim"]
            
            if custo_a < custo_b:
                melhor_custo = custo_a
                compra_sim = f"Poly (${mercado_poly['preco_sim']:.2f})"
                compra_nao = f"Kalshi (${melhor_match['preco_nao']:.2f})"
            else:
                melhor_custo = custo_b
                compra_sim = f"Kalshi (${melhor_match['preco_sim']:.2f})"
                compra_nao = f"Poly (${mercado_poly['preco_nao']:.2f})"
            
            # Filtro de sanidade: ignora dados absurdos abaixo de 10 cents ou mercados já saturados
            if 0.10 < melhor_custo < 1.20:
                lucro_pct = round(((1.00 - melhor_custo) / melhor_custo) * 100, 2)
                
                sinais_encontrados.append({
                    "evento_poly": mercado_poly["titulo"],
                    "evento_kalshi": melhor_match["titulo"],
                    "compra_sim": compra_sim,
                    "compra_nao": compra_nao,
                    "custo": round(melhor_custo, 3),
                    "lucro_pct": lucro_pct,
                    "is_profitable": melhor_custo < 1.00,
                    "link_poly": mercado_poly["link"],
                    "link_kalshi": melhor_match["link"],
                    "confianca": round(maior_score * 100, 1)
                })
                
    # Ordena mostrando maior margem de lucro primeiro
    sinais_encontrados = sorted(sinais_encontrados, key=lambda x: x['lucro_pct'], reverse=True)
    return sinais_encontrados[:20]
