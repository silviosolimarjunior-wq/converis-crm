from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'converis_secret_key'
DB_NAME = ':memory:'

CONTRATOS_POR_SERVICO = {
    "Lei do Superendividamento": "Contrato de Superendividamento",
    "Empréstimo Consignado do INSS": "Contrato de Revisão Consignado",
    "Dívida do Cartão de Crédito": "Contrato de Renegociação de Cartão",
    "Parcelas Atrasadas (Financiamentos)": "Contrato de Defesa de Financiamento"
}

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            servico TEXT,
            telefone TEXT,
            valor REAL,
            custo REAL,
            status TEXT,
            tipo_contrato TEXT,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor TEXT,
            mensagem TEXT,
            data_envio DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM leads')
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO leads (nome, servico, telefone, valor, custo, status, tipo_contrato) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Silvio Solimar Silva", "Parcelas Atrasadas (Financiamentos)", "51990113071", 1500.00, 300.00, "Vendas", "Contrato de Defesa de Financiamento"))
        cursor.execute("""
            INSERT INTO leads (nome, servico, telefone, valor, custo, status, tipo_contrato) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Maria Oliveira", "Lei do Superendividamento", "51988887777", 2500.00, 500.00, "Contrato Fechado", "Contrato de Superendividamento"))
        cursor.execute("""
            INSERT INTO leads (nome, servico, telefone, valor, custo, status, tipo_contrato) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("João Santos", "Empréstimo Consignado do INSS", "51977776666", 800.00, 150.00, "Pré-Venda", "Contrato de Revisão Consignado"))
        conn.commit()
    conn.close()

init_db()

catalogo_servicos = [
    {"titulo": "Lei do Superendividamento", "desc": "Como Renegociar Dívidas e Proteger o seu Mínimo Existencial."},
    {"titulo": "Empréstimo Consignado do INSS", "desc": "Redução de até 50% na parcela com análise completa de contratos."},
    {"titulo": "Dívida do Cartão de Crédito", "desc": "Soluções para juros altos, pagamento mínimo e renegociação de faturas."},
    {"titulo": "Parcelas Atrasadas (Financiamentos)", "desc": "Soluções judiciais e extrajudiciais para veículos e consórcios."}
]

FORM_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Soluções Financeiras</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .box { background: #1c2541; padding: 30px; border-radius: 12px; border: 1px solid #3a506b; width: 100%; max-width: 450px; text-align: center; }
        .logo-badge { background: #7209b7; color: white; width: 60px; height: 60px; border-radius: 15px; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; margin: 0 auto 20px; }
        h1 { color: #ffb703; font-size: 24px; margin-bottom: 10px; }
        p { color: #8d99ae; font-size: 14px; margin-bottom: 25px; }
        .form-group { text-align: left; margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-size: 13px; color: #8d99ae; }
        input { width: 100%; padding: 12px; background: #0b132b; border: 1px solid #3a506b; color: white; border-radius: 6px; font-size: 14px; }
        button { background: #ffb703; color: #0b132b; border: none; padding: 14px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; font-size: 16px; margin-top: 15px; }
        .team-link { display: block; margin-top: 20px; color: #2ec4b6; font-size: 12px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="box">
        <div class="logo-badge">∞</div>
        <h1>🏠 CONVERIS</h1>
        <p>Preencha os seus dados para iniciar o atendimento.</p>
        <form action="/etapa2" method="POST">
            <div class="form-group">
                <label>O seu Nome Completo *</label>
                <input type="text" name="nome" required placeholder="Digite o seu nome">
            </div>
            <div class="form-group">
                <label>O seu WhatsApp / Telefone *</label>
                <input type="text" name="telefone" required placeholder="51999999999">
            </div>
            <button type="submit">Avançar para Catálogo de Serviços 📦</button>
        </form>
        <a href="/painel" class="team-link">🔒 Área da Equipe (CRM)</a>
    </div>
</body>
</html>
'''

SERVICE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Catálogo de Serviços</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .box { background: #1c2541; padding: 25px; border-radius: 12px; border: 1px solid #3a506b; width: 100%; max-width: 550px; text-align: center; }
        h1 { color: #ffb703; font-size: 22px; margin-bottom: 8px; }
        p { color: #8d99ae; font-size: 13px; margin-bottom: 20px; }
        .service-btn { background: #0b132b; color: white; border: 1px solid #3a506b; padding: 14px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; font-size: 15px; margin-bottom: 12px; text-align: left; transition: 0.2s; display: block; text-decoration: none; }
        .service-btn:hover { background: #ffb703; color: #0b132b; border-color: #ffb703; }
    </style>
</head>
<body>
    <div class="box">
        <h1>📦 Catálogo de Serviços</h1>
        <p>Escolha o tipo de serviço que deseja contratar:</p>
        <form action="/etapa3" method="POST">
            {% for serv in servicos %}
            <button name="servico" value="{{ serv.titulo }}" class="service-btn">
                <strong>{{ serv.titulo }}</strong><br>
                <span style="font-size: 12px; color: #8d99ae; font-weight: normal;">{{ serv.desc }}</span>
            </button>
            {% endfor %}
        </form>
    </div>
</body>
</html>
'''

REDIRECT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecionando...</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .box { background: #1c2541; padding: 40px; border-radius: 12px; border: 1px solid #3a506b; width: 100%; max-width: 450px; text-align: center; }
        .spinner { border: 4px solid #3a506b; border-top: 4px solid #ffb703; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        h1 { color: #ffb703; font-size: 22px; margin-bottom: 15px; }
        p { color: #8d99ae; font-size: 14px; line-height: 1.5; }
    </style>
    <script>
        setTimeout(function() { window.location.href = "{{ whatsapp_url }}"; }, 3500);
    </script>
</head>
<body>
    <div class="box">
        <div class="spinner"></div>
        <h1>Tudo pronto!</h1>
        <p>A ser encaminhado para um consultor especialista da Converis via WhatsApp...</p>
    </div>
</body>
</html>
'''

PANEL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Painel da Equipa</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; margin: 0; padding: 0; }
        header { background: #0b132b; padding: 15px 20px; border-bottom: 2px solid #ffb703; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
        .logo-area { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background: #7209b7; color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; }
        .nav-tools { display: flex; gap: 8px; flex-wrap: wrap; }
        .container { max-width: 1100px; margin: 15px auto; padding: 10px; }
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .card-metric { background: #1c2541; padding: 16px; border-radius: 8px; border: 1px solid #3a506b; }
        .card-metric h3 { margin: 0 0 8px 0; font-size: 11px; color: #8d99ae; }
        .card-metric .value { font-size: 20px; font-weight: bold; }
        .section-box { background: #1c2541; padding: 18px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #3a506b; }
        .section-box h3 { margin-top: 0; color: #ffb703; font-size: 16px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #3a506b; padding-bottom: 8px; }
        .lead-card { background: #0b132b; border: 1px solid #3a506b; padding: 12px; border-radius: 8px; margin-bottom: 12px; }
        .btn-whats { background: #2ec4b6; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; }
        .btn-action { background: #ffb703; color: #0b132b; padding: 6px 12px; border-radius: 4px; border: none; font-size: 12px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 5px; }
        .btn-tool { background: #3a506b; color: #ffffff; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; border: 1px solid #ffb703; display: inline-flex; align-items: center; gap: 4px; }
        .badge-status { padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        .badge-prevenda { background: #ffb703; color: #0b132b; }
        .badge-vendas { background: #4cc9f0; color: #0b132b; }
        .badge-fechado { background: #7209b7; color: white; }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-badge">∞</div>
            <div>
                <h2 style="margin:0; font-size:18px;">CONVERIS CRM</h2>
                <span style="font-size:11px; color: #8d99ae;">PAINEL DE GESTÃO INTEGRADA</span>
            </div>
        </div>
        <div class="nav-tools">
            <a href="/" class="btn-tool">🏠 Início</a>
            <a href="/catalogo" class="btn-tool">📦 Catálogo</a>
            <a href="/treinamento" class="btn-tool">🎓 Treinamento</a>
            <a href="/chat_equipa" class="btn-tool">💬 Chat ao Vivo</a>
            <a href="/dre" class="btn-tool" style="border-color: #2ec4b6;">📊 DRE Corporativa</a>
        </div>
    </header>

    <div class="container">
        <div class="section-box">
            <h3>🏠 Dashboard - Resumo Geral</h3>
            <div class="grid-cards" style="margin-bottom:0;">
                <div class="card-metric">
                    <h3>⏳ PRÉ-VENDA (ESPERA)</h3>
                    <div class="value" style="color: #ffb703;">{{ total_prevenda }}</div>
                </div>
                <div class="card-metric">
                    <h3>🤝 VENDAS (EM ATENDIMENTO)</h3>
                    <div class="value" style="color: #4cc9f0;">{{ total_vendas }}</div>
                </div>
                <div class="card-metric">
                    <h3>✅ CONCLUÍDAS / CONTRATOS</h3>
                    <div class="value" style="color: #2ec4b6;">{{ total_fechados }}</div>
                </div>
                <div class="card-metric">
                    <h3>💰 FATURAMENTO BRUTO</h3>
                    <div class="value" style="color: #ffb703;">R$ {{ "%.2f"|format(faturamento) }}</div>
                </div>
            </div>
        </div>

        <div class="section-box">
            <h3>📋 Gestão de Leads & Funil de Atendimento</h3>
            
            <h4 style="color: #ffb703; font-size: 14px; margin-bottom: 8px;">⏳ Pré-Venda (Aguardando Primeiro Contato)</h4>
            {% if leads_prevenda %}
                {% for lead in leads_prevenda %}
                <div class="lead-card" style="border-left: 4px solid #ffb703;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{{ lead['nome'] }}</strong>
                        <span class="badge-status badge-prevenda">{{ lead['status'] }}</span>
                    </div>
                    <span style="color: #8d99ae; font-size: 12px;">📁 Serviço: {{ lead['servico'] }}</span><br>
                    <span style="color: #8d99ae; font-size: 12px;">📞 Tel: {{ lead['telefone'] }}</span><br>
                    <span style="color: #4cc9f0; font-size: 12px;">📝 Contrato: {{ lead['tipo_contrato'] }}</span>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px;">
                        <a href="https://wa.me/{{ lead['telefone'] }}?text=Olá%20{{ lead['nome'] }},%20sou%20da%20Converis." target="_blank" class="btn-whats">📱 WhatsApp</a>
                        <a href="/atualizar_status/{{ lead['id'] }}/Vendas" class="btn-action">🤝 Mover p/ Vendas</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #8d99ae; font-size: 12px; font-style: italic;">Nenhum lead em Pré-Venda.</p>
            {% endif %}

            <h4 style="color: #4cc9f0; font-size: 14px; margin-top: 25px; margin-bottom: 8px;">🤝 Vendas (Em Negociação Ativa)</h4>
            {% if leads_vendas %}
                {% for lead in leads_vendas %}
                <div class="lead-card" style="border-left: 4px solid #4cc9f0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{{ lead['nome'] }}</strong>
                        <span class="badge-status badge-vendas">{{ lead['status'] }}</span>
                    </div>
                    <span style="color: #8d99ae; font-size: 12px;">📁 Serviço: {{ lead['servico'] }}</span><br>
                    <span style="color: #8d99ae; font-size: 12px;">📞 Tel: {{ lead['telefone'] }}</span><br>
                    <div style="color: #ffb703; font-weight: bold; margin-top: 4px;">Valor: R$ {{ "%.2f"|format(lead['valor']) }}</div>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px;">
                        <a href="https://wa.me/{{ lead['telefone'] }}" target="_blank" class="btn-whats">📱 WhatsApp</a>
                        <a href="/atualizar_status/{{ lead['id'] }}/Contrato_Fechado" class="btn-action" style="background: #2ec4b6; color: #0b132b;">✅ Concluir / Fechar Contrato</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #8d99ae; font-size: 12px; font-style: italic;">Nenhum lead em fase de Vendas.</p>
            {% endif %}

            <h4 style="color: #2ec4b6; font-size: 14px; margin-top: 25px; margin-bottom: 8px;">📄 Contratos Fechados (Concluídas)</h4>
            {% if contratos_lista %}
                {% for c in contratos_lista %}
                <div class="lead-card" style="border-left: 4px solid #7209b7;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{{ c['nome'] }}</strong>
                        <span class="badge-status badge-fechado">Fechado</span>
                    </div>
                    <span style="color: #8d99ae; font-size: 12px;">📁 Serviço: {{ c['servico'] }}</span><br>
                    <span style="color: #2ec4b6; font-size: 12px; font-weight: bold;">📄 Documento: {{ c['tipo_contrato'] }}</span><br>
                    <span style="color: #ffb703; font-size: 12px;">Valor Fechado: R$ {{ "%.2f"|format(c['valor']) }}</span>
                    <div style="margin-top: 10px;">
                        <a href="/ver_contrato/{{ c['id'] }}" target="_blank" class="btn-action" style="background: #2ec4b6; color: #0b132b;">👁️ Ver Contrato Emitido</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #8d99ae; font-size: 12px; font-style: italic;">Nenhum contrato fechado ainda.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

DRE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - DRE Corporativa</title>
    <style>
        body { background-color: #0b132b; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }
        .box { background: #1c2541; padding: 25px; border-radius: 12px; border: 1px solid #3a506b; max-width: 800px; margin: 0 auto; }
        h1 { color: #ffb703; font-size: 22px; margin-top: 0; border-bottom: 2px solid #3a506b; padding-bottom: 10px; }
        .dre-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .dre-table th, .dre-table td { padding: 12px; text-align: left; border-bottom: 1px solid #3a506b; }
        .dre-table th { background-color: #0b132b; color: #2ec4b6; }
        .row-total { font-weight: bold; background-color: #0b132b; color: #ffb703; }
        .row-lucro { font-weight: bold; background-color: #2ec4b6; color: #0b132b; }
        .btn-voltar { background: #ffb703; color: #0b132b; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>📊 DRE Corporativa (Demonstração do Resultado do Exercício)</h1>
        <p style="color: #8d99ae;">Relatório financeiro em tempo real dos contratos fechados.</p>
        
        <table class="dre-table">
            <thead>
                <tr>
                    <th>Descrição do Item</th>
                    <th style="text-align: right;">Valor (R$)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>(+) Receita Bruta de Vendas (Contratos Fechados)</strong></td>
                    <td style="text-align: right; color: #2ec4b6;">R$ {{ "%.2f"|format(receita_bruta) }}</td>
                </tr>
                <tr>
                    <td>(-) Custos Operacionais Directos</td>
                    <td style="text-align: right; color: #e63946;">R$ {{ "%.2f"|format(custos_totais) }}</td>
                </tr>
                <tr class="row-total">
                    <td>(=) Margem de Contribuição / Resultado Bruto</td>
                    <td style="text-align: right;">R$ {{ "%.2f"|format(lucro_liquido) }}</td>
                </tr>
                <tr>
                    <td>(-) Despesas Administrativas e Comercialização (Impostos/Taxas ~10%)</td>
                    <td style="text-align: right; color: #e63946;">R$ {{ "%.2f"|format(receita_bruta * 0.10) }}</td>
                </tr>
                <tr class="row-lucro">
                    <td>(=) LUCRO LÍQUIDO OPERACIONAL</td>
                    <td style="text-align: right;">R$ {{ "%.2f"|format(lucro_liquido - (receita_bruta * 0.10)) }}</td>
                </tr>
            </tbody>
        </table>

        <a href="/painel" class="btn-voltar">← Voltar ao CRM</a>
    </div>
</body>
</html>
'''

CONTRATO_VIEW_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Contrato Gerado</title>
    <style>
        body { background-color: #0b132b; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; display: flex; justify-content: center; }
        .contract-box { background: #1c2541; padding: 30px; border-radius: 12px; border: 1px solid #3a506b; width: 100%; max-width: 700px; }
        h1 { color: #ffb703; font-size: 22px; border-bottom: 2px solid #3a506b; padding-bottom: 10px; margin-top: 0; }
        p { line-height: 1.6; color: #d8dee9; font-size: 14px; }
        .btn-voltar { background: #ffb703; color: #0b132b; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="contract-box">
        <h1>📄 {{ lead['tipo_contrato'] }}</h1>
        <p><strong>Contratante (Cliente):</strong> {{ lead['nome'] }}</p>
        <p><strong>Telefone / WhatsApp:</strong> {{ lead['telefone'] }}</p>
        <p><strong>Serviço Contratado:</strong> {{ lead['servico'] }}</p>
        <hr style="border-color: #3a506b; margin: 20px 0;">
        <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO:</strong> O presente instrumento tem como objeto a prestação de serviços especializados de assessoria financeira referentes a <em>{{ lead['servico'] }}</em>, prestados pela CONVERIS SOLUÇÕES FINANCEIRAS.</p>
        <p><strong>CLÁUSULA SEGUNDA - DOS HONORÁRIOS:</strong> O valor acordado para a prestação dos serviços é de R$ {{ "%.2f"|format(lead['valor']) }}, pagos conforme acerto prévio.</p>
        <p><strong>CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES:</strong> A CONVERIS compromete-se a envidar todos os esforços técnicos e legais para o sucesso da demanda do cliente.</p>
        <br>
        <p style="text-align: center; color: #2ec4b6; font-weight: bold; border: 1px dashed #2ec4b6; padding: 10px; border-radius: 6px;">✅ Documento gerado eletronicamente e validado pelo CRM Converis.</p>
        <a href="/painel" class="btn-voltar">← Voltar ao CRM</a>
    </div>
</body>
</html>
'''

TREINAMENTO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Central de Treinamento</title>
    <style>
        body { background-color: #0b132b; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }
        .box { background: #1c2541; padding: 25px; border-radius: 12px; border: 1px solid #3a506b; max-width: 800px; margin: 0 auto; }
        h1 { color: #ffb703; font-size: 22px; margin-top: 0; }
        .card-aula { background: #0b132b; border: 1px solid #3a506b; padding: 15px; border-radius: 8px; margin-bottom: 12px; }
        .btn-voltar { background: #ffb703; color: #0b132b; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎓 Central de Treinamento & Scripts Comercial</h1>
        <p style="color: #8d99ae;">Diretrizes de atendimento e abordagens para conversão de leads.</p>
        
        <div class="card-aula">
            <h3 style="color: #2ec4b6; margin-top: 0;">1. Abordagem Inicial - Superendividamento</h3>
            <p style="font-size: 13px; color: #d8dee9;">"Olá! Analisamos a sua solicitação. O nosso objetivo é proteger o seu mínimo existencial e repactuar os débitos em condições sustentáveis..."</p>
        </div>

        <div class="card-aula">
            <h3 style="color: #2ec4b6; margin-top: 0;">2. Quebra de Objeções em Financiamentos</h3>
            <p style="font-size: 13px; color: #d8dee9;">"A revisão contratual visa recalcular encargos abusivos para viabilizar a quitação ou regularização das parcelas atrasadas..."</p>
        </div>

        <a href="/painel" class="btn-voltar">← Voltar ao CRM</a>
    </div>
</body>
</html>
'''

CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Chat ao Vivo</title>
    <style>
        body { background-color: #0b132b; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }
        .box { background: #1c2541; padding: 25px; border-radius: 12px; border: 1px solid #3a506b; max-width: 600px; margin: 0 auto; }
        h1 { color: #ffb703; font-size: 22px; margin-top: 0; }
        .chat-box { background: #0b132b; border: 1px solid #3a506b; padding: 15px; border-radius: 8px; height: 280px; overflow-y: auto; margin-bottom: 15px; }
        .msg { margin-bottom: 10px; font-size: 13px; }
        .msg strong { color: #2ec4b6; }
        .msg span { font-size: 10px; color: #8d99ae; margin-left: 5px; }
        input, button { padding: 10px; border-radius: 6px; border: 1px solid #3a506b; }
        input { background: #0b132b; color: white; width: 70%; }
        button { background: #ffb703; color: #0b132b; font-weight: bold; width: 27%; cursor: pointer; }
        .btn-voltar { background: #3a506b; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 15px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>💬 Chat ao Vivo da Equipa</h1>
        <div class="chat-box">
            {% for msg in mensagens %}
            <div class="msg">
                <strong>{{ msg['autor'] }}:</strong> {{ msg['mensagem'] }} <span>({{ msg['data_envio'] }})</span>
            </div>
            {% endfor %}
        </div>
        <form action="/enviar_chat" method="POST" style="display: flex; gap: 3%;">
            <input type="text" name="mensagem" placeholder="Digite uma mensagem..." required>
            <button type="submit">Enviar</button>
        </form>
        <a href="/painel" class="btn-voltar">← Voltar ao CRM</a>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(FORM_TEMPLATE)

@app.route('/catalogo')
def catalogo():
    return render_template_string(SERVICE_TEMPLATE, servicos=catalogo_servicos)

@app.route('/etapa2', methods=['POST'])
def etapa2():
    session['nome'] = request.form.get('nome')
    session['telefone'] = request.form.get('telefone')
    return render_template_string(SERVICE_TEMPLATE, servicos=catalogo_servicos)

@app.route('/etapa3', methods=['POST'])
def etapa3():
    servico = request.form.get('servico')
    nome = session.get('nome', 'Cliente')
    telefone = session.get('telefone', '')
    tipo_contrato = CONTRATOS_POR_SERVICO.get(servico, "Contrato Geral de Prestação de Serviços")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (nome, servico, telefone, valor, custo, status, tipo_contrato) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, servico, telefone, 1200.00, 200.00, "Pré-Venda", tipo_contrato))
    conn.commit()
    conn.close()

    mensagem = f"Olá, meu nome é {nome}. Gostaria de atendimento sobre: {servico}."
    whatsapp_url = f"https://wa.me/5551999797731?text={mensagem}"
    return render_template_string(REDIRECT_TEMPLATE, whatsapp_url=whatsapp_url)

@app.route('/painel')
def painel_equipe():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM leads WHERE status = 'Pré-Venda' ORDER BY id DESC")
    leads_prevenda = cursor.fetchall()
    
    cursor.execute("SELECT * FROM leads WHERE status = 'Vendas' ORDER BY id DESC")
    leads_vendas = cursor.fetchall()
    
    cursor.execute("SELECT * FROM leads WHERE status = 'Contrato Fechado' ORDER BY id DESC")
    contratos_lista = cursor.fetchall()
    
    cursor.execute("SELECT SUM(valor) FROM leads WHERE status = 'Contrato Fechado'")
    res = cursor.fetchone()[0]
    faturamento = res if res else 0.0
    
    conn.close()
    
    return render_template_string(
        PANEL_TEMPLATE, 
        leads_prevenda=leads_prevenda,
        leads_vendas=leads_vendas,
        contratos_lista=contratos_lista,
        total_prevenda=len(leads_prevenda),
        total_vendas=len(leads_vendas),
        total_fechados=len(contratos_lista),
        faturamento=faturamento
    )

@app.route('/dre')
def dre():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) as receita, SUM(custo) as custo FROM leads WHERE status = 'Contrato Fechado'")
    row = cursor.fetchone()
    conn.close()
    
    receita_bruta = row['receita'] if row['receita'] else 0.0
    custos_totais = row['custo'] if row['custo'] else 0.0
    lucro_liquido = receita_bruta - custos_totais
    
    return render_template_string(DRE_TEMPLATE, receita_bruta=receita_bruta, custos_totais=custos_totais, lucro_liquido=lucro_liquido)

@app.route('/treinamento')
def treinamento():
    return render_template_string(TREINAMENTO_TEMPLATE)

@app.route('/chat_equipa')
def chat_equipa():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_mensagens ORDER BY id DESC LIMIT 20")
    mensagens = cursor.fetchall()
    conn.close()
    return render_template_string(CHAT_TEMPLATE, mensagens=reversed(mensagens))

@app.route('/enviar_chat', methods=['POST'])
def enviar_chat():
    msg = request.form.get('mensagem')
    if msg:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_mensagens (autor, mensagem) VALUES (?, ?)", ("Aquiles", msg))
        conn.commit()
        conn.close()
    return redirect(url_for('chat_equipa'))

@app.route('/atualizar_status/<int:lead_id>/<path:novo_status>')
def atualizar_status(lead_id, novo_status):
    status_formatado = novo_status.replace('_', ' ')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (status_formatado, lead_id))
    conn.commit()
    conn.close()
    return redirect(url_for('painel_equipe'))

@app.route('/ver_contrato/<int:lead_id>')
def ver_contrato(lead_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    lead = cursor.fetchone()
    conn.close()
    if lead:
        return render_template_string(CONTRATO_VIEW_TEMPLATE, lead=lead)
    return "Contrato não encontrado", 404

if __name__ == '__main__':
    app.run(port=5000)
