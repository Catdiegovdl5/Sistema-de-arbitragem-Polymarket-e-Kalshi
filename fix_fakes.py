import re

path = 'immike_bot/run_with_dashboard.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_fakes = """                    fake_markets = [
                        ("Will Bitcoin hit $100k?", "Bitcoin > $100,000?"),
                        ("Ethereum ETF Approved in 2026?", "ETH ETF 2026"),
                        ("Will Donald Trump win the 2028 Election?", "Trump 2028"),
                        ("SPY to hit 600 by EOY?", "SPY > 600"),
                        ("Will Elon Musk buy another social network?", "Musk Social Network"),
                        ("Real Madrid to win Champions League?", "Real Madrid UCL"),
                    ]"""

new_fakes = """                    fake_markets = [
                        ("Will Bitcoin hit $100k?", "Bitcoin > $100,000?"),
                        ("Ethereum ETF Approved in 2026?", "ETH ETF 2026"),
                        ("Will Donald Trump win the 2028 Election?", "Trump 2028"),
                        ("US Inflation (CPI) drops below 2%?", "CPI < 2%"),
                        ("Fed cuts rate by 50bps?", "Fed 50bps cut"),
                        ("Real Madrid to win Champions League?", "Real Madrid UCL"),
                        ("Will a Category 5 hurricane hit Florida?", "FL Hurricane Cat 5"),
                    ]"""

content = content.replace(old_fakes, new_fakes)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated fake data!")
