import re

index_path = 'black_dashboard/templates/home/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the old tabs block with the new one
old_tabs_pattern = r'<div class="btn-group btn-group-toggle" data-toggle="buttons">[\s\S]*?</div>'

new_tabs_html = """<div class="btn-group btn-group-toggle" data-toggle="buttons">
                <label class="btn btn-sm btn-success btn-simple active" onclick="window.currentCategory='all'; forceRefresh();">
                  <input type="radio" name="options" checked>
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Todos</span>
                  <span class="d-block d-sm-none"><i class="fa fa-list"></i></span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='politica'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Política</span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='economia'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Economia</span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='esportes'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Esportes</span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='cripto'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Cripto</span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='clima'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Clima</span>
                </label>
              </div>"""

content = re.sub(old_tabs_pattern, new_tabs_html, content, count=1)

# Replace the JS filtering logic
old_js_pattern = r"const q = opp\.market_pair\.polymarket_question\.toLowerCase\(\);[\s\S]*?if \(window\.currentCategory !== 'all' && window\.currentCategory !== cat\) return;"

new_js_logic = """const q = opp.market_pair.polymarket_question.toLowerCase();
            let cat = 'outros';
            if (q.includes('bitcoin') || q.includes('eth') || q.includes('crypto')) cat = 'cripto';
            else if (q.includes('trump') || q.includes('election') || q.includes('kamala') || q.includes('biden') || q.includes('vote') || q.includes('governor')) cat = 'politica';
            else if (q.includes('madrid') || q.includes('league') || q.includes('champions') || q.includes('vs') || q.includes('fc') || q.includes('win the') || q.includes('nba') || q.includes('nfl')) cat = 'esportes';
            else if (q.includes('inflation') || q.includes('fed') || q.includes('rate') || q.includes('economy') || q.includes('gdp') || q.includes('job') || q.includes('cpi')) cat = 'economia';
            else if (q.includes('weather') || q.includes('temperature') || q.includes('rain') || q.includes('hurricane') || q.includes('storm')) cat = 'clima';
            
            if (window.currentCategory !== 'all' && window.currentCategory !== cat) return;"""

content = re.sub(old_js_pattern, new_js_logic, content)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated tabs and JS!")
