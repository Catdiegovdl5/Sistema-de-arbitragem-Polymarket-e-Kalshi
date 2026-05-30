import re

index_path = 'black_dashboard/templates/home/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

# Fix polyLink back to /event/
old_polyLink = r"const polyLink = `https://polymarket.com/markets\?query=\$\{encodeURIComponent\(opp\.market_pair\.polymarket_question\)\}`;|" + \
               r"const polyLink = `https://polymarket\.com/markets\?query=\$\{encodeURIComponent\(opp\.market_pair\.polymarket_question\)\}`;|" + \
               r"const polyLink = `https://polymarket\.com/market/\$\{opp\.market_pair\.polymarket_id\}`;|" + \
               r"const polyLink = `https://polymarket.com/markets\?query=\$\{encodeURIComponent\(opp.market_pair.polymarket_question\)\}`;|" + \
               r"const polyLink = `https://polymarket\.com/markets\?query=\$\{encodeURIComponent\(opp\.market_pair\.polymarket_question\)\}`;|" + \
               r"const polyLink = `https://polymarket.com/markets\?query=\$\{encodeURIComponent\(opp.market_pair.polymarket_question\)\}`;"

# To be safe, just replace the line exactly
lines = index_content.split('\n')
for i, line in enumerate(lines):
    if 'const polyLink = `https://polymarket.com/markets?query=' in line:
        lines[i] = "            const polyLink = `https://polymarket.com/event/${opp.market_pair.polymarket_id}`;"
    elif 'const polyLink = `https://polymarket.com/market/' in line:
        lines[i] = "            const polyLink = `https://polymarket.com/event/${opp.market_pair.polymarket_id}`;"

index_content = '\n'.join(lines)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_content)


dash_path = 'immike_bot/run_with_dashboard.py'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_content = f.read()

old_fakes = """                    fake_markets = [
                        ("Will Bitcoin hit $100k?", "Bitcoin > $100,000?"),
                        ("Ethereum ETF Approved in 2026?", "ETH ETF 2026"),
                        ("Will Donald Trump win the 2028 Election?", "Trump 2028"),
                        ("US Inflation (CPI) drops below 2%?", "CPI < 2%"),
                        ("Fed cuts rate by 50bps?", "Fed 50bps cut"),
                        ("Real Madrid to win Champions League?", "Real Madrid UCL"),
                        ("Will a Category 5 hurricane hit Florida?", "FL Hurricane Cat 5"),
                    ]
                    poly_q, kalshi_t = random.choice(fake_markets)"""

new_fakes = """                    fake_markets = [
                        ("Will Bitcoin hit $100k?", "Bitcoin > $100,000?", "will-bitcoin-reach-100k-in-2024"),
                        ("Ethereum ETF Approved?", "ETH ETF", "ethereum-etf-approval"),
                        ("Will Donald Trump win the Election?", "Trump 2024", "presidential-election-winner-2024"),
                        ("US Inflation (CPI) drops below 2%?", "CPI < 2%", "us-core-cpi-inflation"),
                        ("Fed cuts rate by 50bps?", "Fed 50bps cut", "fed-interest-rate-decision"),
                        ("Real Madrid to win Champions League?", "Real Madrid UCL", "champions-league-winner"),
                        ("Will a Category 5 hurricane hit Florida?", "FL Hurricane Cat 5", "category-5-hurricane-us"),
                    ]
                    poly_q, kalshi_t, poly_id = random.choice(fake_markets)"""

dash_content = dash_content.replace(old_fakes, new_fakes)

# Also need to make sure poly_id isn't unconditionally overwritten
# "poly_id = 'test_poly'" is right above fake_markets
dash_content = dash_content.replace('poly_id = "test_poly"', '# poly_id = "test_poly"')

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(dash_content)

print("Fixed links!")
