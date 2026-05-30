import re

# 1. Update index.html
index_path = 'black_dashboard/templates/home/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

tabs_html = """
              <div class="btn-group btn-group-toggle" data-toggle="buttons">
                <label class="btn btn-sm btn-success btn-simple active" onclick="window.currentCategory='all'; forceRefresh();">
                  <input type="radio" name="options" checked>
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Todos</span>
                  <span class="d-block d-sm-none"><i class="fa fa-list"></i></span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='cripto'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Criptomoedas</span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='politica'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Política</span>
                </label>
                <label class="btn btn-sm btn-success btn-simple" onclick="window.currentCategory='esportes'; forceRefresh();">
                  <input type="radio" name="options">
                  <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">Esportes</span>
                </label>
              </div>
"""

# Replace the empty <div class="col-sm-6 text-left">
index_content = re.sub(
    r'<div class="col-sm-6 text-left">\s*</div>',
    f'<div class="col-sm-6 text-left">{tabs_html}</div>',
    index_content
)

# Update Javascript
js_old_polylink = r'const polyLink = `https://polymarket.com/market/\$\{opp.market_pair.polymarket_id\}`;'
js_new_polylink = r'const polyLink = `https://polymarket.com/markets?query=${encodeURIComponent(opp.market_pair.polymarket_question)}`;'
index_content = index_content.replace(js_old_polylink, js_new_polylink)

js_filter_code = """
        window.currentCategory = window.currentCategory || 'all';
        opps.forEach(opp => {
            const q = opp.market_pair.polymarket_question.toLowerCase();
            let cat = 'outros';
            if (q.includes('bitcoin') || q.includes('eth') || q.includes('crypto')) cat = 'cripto';
            else if (q.includes('trump') || q.includes('election') || q.includes('kamala') || q.includes('biden') || q.includes('vote')) cat = 'politica';
            else if (q.includes('madrid') || q.includes('league') || q.includes('champions') || q.includes('vs')) cat = 'esportes';
            
            if (window.currentCategory !== 'all' && window.currentCategory !== cat) return;
            
            const polyLink = `https://polymarket.com/markets?query=${encodeURIComponent(opp.market_pair.polymarket_question)}`;
"""

index_content = re.sub(
    r'opps\.forEach\(opp => \{\s*const polyLink[^;]+;',
    js_filter_code,
    index_content
)

# Add a forceRefresh function
forceRefresh_code = """
  function forceRefresh() {
      // Immediate fetch on tab change
      // handled by interval naturally or we can dispatch
  }
  setInterval(() => {
"""
index_content = index_content.replace('setInterval(() => {', forceRefresh_code)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

# 2. Update base.html to change background to Black
base_path = 'black_dashboard/templates/layouts/base.html'
with open(base_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

black_bg_css = """
        body, .wrapper, .main-panel, .sidebar, .off-canvas-sidebar {
            background: #000000 !important;
            background-image: none !important;
        }
        .card {
            background: #111111 !important;
        }
"""
base_content = base_content.replace('/* Minimalist Dark Sidebar */', '/* Minimalist Dark Sidebar */\n' + black_bg_css)

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(base_content)

print("HTML and CSS modifications completed.")
