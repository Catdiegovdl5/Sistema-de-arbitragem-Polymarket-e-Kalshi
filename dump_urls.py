import requests
import json
r = requests.get('http://localhost:8000/api/state')
opps = r.json().get('cross_platform', {}).get('cross_opportunities', [])
for opp in opps:
    poly_link = f"https://polymarket.com/event/{opp['market_pair'].get('polymarket_slug')}"
    kalshi_link = f"https://kalshi.com/markets/{opp['market_pair'].get('kalshi_ticker')}"
    print('Poly:', poly_link)
    print('Kalshi:', kalshi_link)
