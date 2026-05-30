with open('c:/Users/99196/OneDrive/Documentos/SISTEMA DE ARBITRAGE/black_dashboard/templates/home/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

bad_start = text.find('{% extends "layouts/base.html" %}', 10)
if bad_start != -1:
    good_text = text[:bad_start]
    correct_script = """            if (tbody.children.length === 0 || tbody.children[0].innerText.includes('Aguardando')) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">Aguardando sinais...</td></tr>';
            }
            return;
        }

        tbody.innerHTML = '';
        
        window.currentCategory = window.currentCategory || 'all';
        opps.forEach(opp => {
            const q = opp.market_pair.polymarket_question.toLowerCase();
            let cat = 'outros';
            if (q.includes('bitcoin') || q.includes('eth') || q.includes('crypto')) cat = 'cripto';
            else if (q.includes('trump') || q.includes('election') || q.includes('kamala') || q.includes('biden') || q.includes('vote') || q.includes('governor')) cat = 'politica';
            else if (q.includes('madrid') || q.includes('league') || q.includes('champions') || q.includes('vs') || q.includes('fc') || q.includes('win the') || q.includes('nba') || q.includes('nfl')) cat = 'esportes';
            else if (q.includes('inflation') || q.includes('fed') || q.includes('rate') || q.includes('economy') || q.includes('gdp') || q.includes('job') || q.includes('cpi')) cat = 'economia';
            else if (q.includes('weather') || q.includes('temperature') || q.includes('rain') || q.includes('hurricane') || q.includes('storm')) cat = 'clima';
            
            if (window.currentCategory !== 'all' && window.currentCategory !== cat) return;
            
            // Polymarket recently moved many markets to /market/ instead of /event/
            const polyLink = `https://polymarket.com/market/${opp.market_pair.polymarket_slug || opp.market_pair.polymarket_id}`;

            // Kalshi often 404s on the exact event ticker, so we use the series ticker which is more stable
            const kTicker = opp.market_pair.kalshi_series_ticker || opp.market_pair.kalshi_ticker;
            // Best fallback is search for Kalshi since exact links often 404
            const kTitleSearch = opp.market_pair.kalshi_title.split(',')[0].replace(/\\s+/g, '+');
            const kalshiLink = `https://kalshi.com/markets?search=${kTitleSearch}`;
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div class="font-weight-bold" style="font-size: 0.9rem;">${opp.market_pair.polymarket_question}</div>
                </td>
                <td><a href="${opp.buy_platform === 'polymarket' ? polyLink : kalshiLink}" target="_blank" class="badge badge-info" style="color: white; text-decoration: none;">${opp.buy_platform.toUpperCase()}</a><br>@ $${opp.buy_price.toFixed(3)}</td>
                <td><a href="${opp.sell_platform === 'polymarket' ? polyLink : kalshiLink}" target="_blank" class="badge badge-primary" style="color: white; text-decoration: none;">${opp.sell_platform.toUpperCase()}</a><br>@ $${opp.sell_price.toFixed(3)}</td>
                <td class="text-center"><span class="win-percentage">${(opp.edge_pct * 100).toFixed(2)}%</span></td>
                <td class="text-center">$${opp.max_size.toFixed(2)}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-success btn-icon" onclick="openCalculator('${opp.buy_platform}', '${opp.sell_platform}', ${opp.buy_price}, ${opp.sell_price}, ${opp.edge_pct})">
                        <i class="fa fa-calculator"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
      })
      .catch(console.error);
    }, 500);
</script>
{% endblock javascripts %}
"""
    with open('c:/Users/99196/OneDrive/Documentos/SISTEMA DE ARBITRAGE/black_dashboard/templates/home/index.html', 'w', encoding='utf-8') as f:
        f.write(good_text + correct_script)
    print('Fixed!')
else:
    print('Not found')
