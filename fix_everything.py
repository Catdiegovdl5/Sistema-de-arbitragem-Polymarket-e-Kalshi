import re

# 1. Models.py
models_path = 'immike_bot/polymarket_client/models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add slug to Market
if 'slug: str = ""' not in content:
    content = content.replace(
        '    question: str\n    description: str = ""',
        '    question: str\n    description: str = ""\n    slug: str = ""'
    )
with open(models_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. api.py
api_path = 'immike_bot/polymarket_client/api.py'
with open(api_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'slug=data.get("slug", ""),' not in content:
    content = content.replace(
        '                description=data.get("description", "") or "",\n',
        '                description=data.get("description", "") or "",\n                slug=data.get("slug", ""),\n'
    )

# Decrease polling delays in stream_orderbook
content = re.sub(r'active_batch_size = \d+', 'active_batch_size = 1000', content)
content = re.sub(r'markets_per_request_batch = \d+', 'markets_per_request_batch = 50', content)
content = re.sub(r'request_delay = [\d\.]+', 'request_delay = 0.02', content)
content = re.sub(r'batch_delay = [\d\.]+', 'batch_delay = 0.1', content)
content = re.sub(r'rotation_delay = [\d\.]+', 'rotation_delay = 0.5', content)

with open(api_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. cross_platform_arb.py
arb_path = 'immike_bot/core/cross_platform_arb.py'
with open(arb_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'polymarket_slug: str = ""' not in content:
    content = content.replace(
        '    polymarket_question: str\n',
        '    polymarket_question: str\n    polymarket_slug: str = ""\n'
    )

if 'polymarket_slug=poly_market.slug,' not in content:
    content = content.replace(
        '                        polymarket_id=poly_market.market_id,\n',
        '                        polymarket_id=poly_market.market_id,\n                        polymarket_slug=getattr(poly_market, "slug", ""),\n'
    )

# Decrease Kalshi delay if it exists
content = re.sub(r'await asyncio\.sleep\(0\.2\)', 'await asyncio.sleep(0.05)', content)

with open(arb_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 4. index.html
html_path = 'black_dashboard/templates/home/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_link = r"const polyLink = `https://polymarket.com/event/\$\{opp\.market_pair\.polymarket_id\}`;"
new_link = r"const polyLink = `https://polymarket.com/event/${opp.market_pair.polymarket_slug || opp.market_pair.polymarket_id}`;"
content = re.sub(old_link, new_link, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 5. run_with_dashboard.py
dash_path = 'immike_bot/run_with_dashboard.py'
with open(dash_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'polymarket_slug=poly_id' not in content:
    content = content.replace(
        '                        "polymarket_question": poly_q,\n',
        '                        "polymarket_question": poly_q,\n                        "polymarket_slug": poly_id,\n'
    )

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied fixes for slug and delays!")
