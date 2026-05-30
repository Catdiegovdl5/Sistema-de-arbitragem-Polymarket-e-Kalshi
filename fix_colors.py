import os

css_path = 'black_dashboard/static/assets/css/black-dashboard.css'
with open(css_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('#e14eca', '#00d231') 
content = content.replace('#ba54f5', '#00a824') 

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(content)

html_path = 'black_dashboard/templates/home/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

html_content = html_content.replace('tim-icons icon-calculator', 'fa fa-calculator')
html_content = html_content.replace('<h5 class="card-category">Tempo Real</h5>', '')
html_content = html_content.replace('<h2 class="card-title">Sinais de Arbitragem Polymarket & Kalshi</h2>', '')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Done!')
