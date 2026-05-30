import requests
import json
try:
    r = requests.get('http://localhost:8000/api/state')
    opps = r.json().get('cross_platform', {}).get('cross_opportunities', [])
    print('Opps length:', len(opps))
    if opps:
        print('Poly URL:', f"https://polymarket.com/market/{opps[0]['market_pair'].get('polymarket_slug')}")
        print('Kalshi Search:', opps[0]['market_pair'].get('kalshi_title').split(',')[0])
except Exception as e:
    print('Error:', e)
