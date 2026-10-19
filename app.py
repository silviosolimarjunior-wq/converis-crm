from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Dados iniciais do CRM
leads = [
    {"id": 1, "nome": "Silvio Solimar", "servico": "Financiamento/Veículos", "telefone": "51990113071", "valor": "54.00", "status": "Novo Lead"}
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Painel de Vendas</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; margin: 0; padding: 0; }
        header { background: #1c2541; padding: 20px; border-bottom: 2px solid #ffb703; display: flex; align-items: center; justify-content: space-between; }
        .logo-area { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background: #7209b7; color: white; width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; }
        .container { max-width: 1100px; margin: 20px auto; padding: 15px; }
        .nav-tabs { display: flex; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }
        .nav-btn { background: #3a506b; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; font-size: 14px; }
        .nav-btn.active { background: #ffb703; color: #0b132b; }
        .nav-btn:hover { opacity: 0.9; }
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .card-metric { background: #1c2541; padding: 20px; border-radius: 10px; border: 1px solid #3a506b; }
        .card-metric h3 { margin: 0 0 10px 0; font-size: 13px; color: #8d99ae; text-transform: uppercase; }
        .card-metric .value { font-size: 24px; font-weight: bold; color: #4cc9f0; }
        .section-box { background: #1c2541; padding: 20px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #3a506b; }
        .section-box h3 { margin-top: 0; color: #ffb703; }
        .lead-card { background: #0b132b; border: 1px solid #3a506b; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-size: 13px; color: #8d99ae; }
        input, select { width: 100%; padding: 12px; background: #0b132b; border: 1px solid #3a506b; color: white; border-radius: 6px; }
        button.submit-btn { background: #ffb703; color: #0b132b; border: none; padding: 12px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; font-size: 15px; }
        button.submit-btn:hover { background: #fb8500; }
        .dre-linha { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #28385e; font-size: 14px; }
        .dre-total { font-weight: bold; color: #4cc9f0; font-size: 16px; margin-top: 10px; }
        .btn-whats { background: #2ec4b6; color: white; padding: 8px 12px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: bold; display: inline-block; margin-top: 10px; }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-badge">∞</div>
            <div>
                <h2 style="margin:0; font-size:20px;">CONVERIS CRM</h2>
                <span style="font-size:11px; color: #8d99ae;">ÁREA DA EQUIPE • AQUILES VENDAS</span>
            </div>
        </div>
    </header>

    <div class="container">
        <!-- Navegação com botão Início -->
        <div class="nav-tabs">
            <a href="/" class="nav-btn active">🏠 Início</a>
            <a href="#" class="nav-btn">📋 Gestão de Leads (Atendimento)</a>
            <a href="#" class="nav-btn">📊 Dashboard</a>
            <a href="#" class="nav-btn">📦 Catálogo</a>
            <a href="#" class="nav-btn">🎓 Treinamento</a>
        </div>

        <div class="grid-cards">
            <div class="card-metric">
                <h3>JÁ RECEBIDO (CAIXA)</h3>
                <div class="value" style="color: #2ec4b6;">R$ 0,00</div>
            </div>
            <div class="card-metric">
                <h3>A RECEBER (FALTA PAGAR)</h3>
                <div class="value" style="color: #ffb703;">R$ 54,00</div>
            </div>
            <div class="card-metric">
                <h3>TOTAL INADIMPLENTE</h3>
                <div class="value" style="color: #e71d36;">R$ 0,00</div>
            </div>
        </div>

        <div class="section-box">
            <h3>➕ Cadastrar Novo Lead Manualmente</h3>
            <form action="/add" method="POST">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div class="form-group">
                        <label>Nome do Cliente *</label>
                        <input type="text" name="nome" required placeholder="Nome do Cliente">
                    </div>
                    <div class="form-group">
                        <label>Serviço (ex: INSS, Cartão)</label>
                        <input type="text" name="servico" required placeholder="Ex: Financiamento/Veículos">
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div class="form-group">
                        <label>WhatsApp</label>
                        <input type="text" name="telefone" required placeholder="51999999999">
                    </div>
                    <div class="form-group">
                        <label>Valor da Dívida (R$)</label>
                        <input type="text" name="valor" required placeholder="54.00">
                    </div>
                </div>
                <button type="submit" class="submit-btn">Adicionar Card</button>
            </form>
        </div>

        <div class="section-box">
            <h3>🔵 Novo Lead (Entrada WhatsApp)</h3>
            {% for lead in leads %}
            <div class="lead-card">
                <strong>{{ lead.nome }}</strong><br>
                <span style="color: #8d99ae; font-size: 13px;">📁 Serviço: {{ lead.servico }}</span><br>
                <span style="color: #8d99ae; font-size: 13px;">📞 Tel: {{ lead.telefone }}</span>
                <div style="color: #2ec4b6; font-weight: bold; margin-top: 5px;">R$ {{ lead.valor }}</div>
                <a href="https://wa.me/{{ lead.telefone }}" target="_blank" class="btn-whats">📲 Falar no Whats</a>
            </div>
            {% endfor %}
        </div>

        <div class="section-box">
            <h3>📊 DRE Corporativa Detalhada</h3>
            <div class="dre-linha">
                <span>(+) Receita Total Contratada</span>
                <span style="color: #2ec4b6;">R$ 54,00</span>
            </div>
            <div class="dre-linha">
                <span>(-) Deduções e Impostos (~8%)</span>
                <span style="color: #e71d36;">R$ 4,32</span>
            </div>
            <div class="dre-linha" style="font-weight: bold; background: #0b132b; padding: 8px;">
                <span>(=) Receita Líquida</span>
                <span>R$ 49,68</span>
            </div>
            <div class="dre-linha">
                <span>(-) Custos e Despesas Operacionais</span>
                <span style="color: #e71d36;">R$ 0,00</span>
            </div>
            <div class="dre-total">
                (=) LUCRO LÍQUIDO DO EXERCÍCIO: <span style="color: #2ec4b6;">R$ 49,68</span>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, leads=leads)

@app.route('/add', methods=['POST'])
def add_lead():
    novo_id = len(leads) + 1
    nome = request.form.get('nome')
    servico = request.form.get('servico')
    telefone = request.form.get('telefone')
    valor = request.form.get('valor')
    leads.append({"id": novo_id, "nome": nome, "servico": servico, "telefone": telefone, "valor": valor, "status": "Novo Lead"})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
