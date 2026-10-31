from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'converis_secret_key_enterprise'

# Na Vercel, o único diretório com permissão de escrita é /tmp
DB_PATH = '/tmp/converis.db'

CONTRATOS_POR_SERVICO = {
    "Lei do Superendividamento": "Contrato de Superendividamento",
    "Empréstimo Consignado do INSS": "Contrato de Revisão Consignado",
    "Dívida do Cartão de Crédito": "Contrato de Renegociação de Cartão",
    "Parcelas Atrasadas (Financiamentos)": "Contrato de Defesa de Financiamento"
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
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
    <title>CONVERIS - Soluções Financeiras Corporativas</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
        body { background-color: #060a17; color: #f8fafc; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .box { background: #0f172a; padding: 35px; border-radius: 16px; border: 1px solid #1e293b; width: 100%; max-width: 460px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }
        .logo-header { display: flex; align-items: center; gap: 12px; margin-bottom: 25px; }
        .logo-badge { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: bold; }
        h1 { color: #f8fafc; font-size: 20px; margin: 0; font-weight: 600; }
        .subtitle { color: #94a3b8; font-size: 13px; margin: 4px 0 0 0; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; line-height: 1.5; }
        .form-group { text-align: left; margin-bottom: 18px; }
        label { display: block; margin-bottom: 6px; font-size: 13px; font-weight: 500; color: #cbd5e1; }
        input { width: 100%; padding: 12px 14px; background: #020617; border: 1px solid #334155; color: white; border-radius: 8px; font-size: 14px; transition: border-color 0.2s; }
        input:focus { outline: none; border-color: #3b82f6; }
        button { background: #3b82f6; color: white; border: none; padding: 14px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%; font-size: 15px; margin-top: 10px; transition: background 0.2s; }
        button:hover { background: #2563eb; }
        .team-link { display: block; margin-top: 25px; color: #38bdf8; font-size: 13px; text-decoration: none; text-align: center; font-weight: 500; }
        .team-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="box">
        <div class="logo-header">
            <div class="logo-badge">C</div>
            <div>
                <h1>CONVERIS</h1>
                <div class="subtitle">Soluções Financeiras & Jurídicas</div>
            </div>
        </div>
        <p>Preencha seus dados cadastrais abaixo para iniciar o atendimento especializado.</p>
        <form action="/etapa2" method="POST">
            <div class="form-group">
                <label>Nome Completo *</label>
                <input type="text" name="nome" required placeholder="Digite o seu nome completo">
            </div>
            <div class="form-group">
                <label>WhatsApp / Telefone de Contato *</label>
                <input type="text" name="telefone" required placeholder="Ex: 51999999999">
            </div>
            <button type="submit">Avançar para Catálogo ➔</button>
        </form>
        <a href="/painel" class="team-link">🔒 Acesso Restrito: Painel Corporativo (CRM)</a>
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
        * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background-color: #060a17; color: #f8fafc; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .box { background: #0f172a; padding: 30px; border-radius: 16px; border: 1px solid #1e293b; width: 100%; max-width: 550px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }
        h1 { color: #f8fafc; font-size: 22px; margin-bottom: 8px; font-weight: 600; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        .service-btn { background: #020617; color: white; border: 1px solid #334155; padding: 16px; border-radius: 10px; cursor: pointer; width: 100%; font-size: 15px; margin-bottom: 12px; text-align: left; transition: all 0.2s; display: block; text-decoration: none; }
        .service-btn:hover { background: #1e293b; border-color: #3b82f6; transform: translateY(-1px); }
        .service-title { font-weight: 600; color: #f8fafc; font-size: 15px; display: block; margin-bottom: 4px; }
        .service-desc { font-size: 12px; color: #94a3b8; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Catálogo de Soluções</h1>
        <p>Selecione a modalidade de serviço desejada para o seu caso:</p>
        <form action="/etapa3" method="POST">
            {% for serv in servicos %}
            <button name="servico" value="{{ serv.titulo }}" class="service-btn">
                <span class="service-title">{{ serv.titulo }}</span>
                <span class="service-desc">{{ serv.desc }}</span>
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
        * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background-color: #060a17; color: #f8fafc; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .box { background: #0f172a; padding: 40px; border-radius: 16px; border: 1px solid #1e293b; width: 100%; max-width: 450px; text-align: center; }
        .spinner { border: 3px solid #1e293b; border-top: 3px solid #3b82f6; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        h1 { color: #f8fafc; font-size: 20px; margin-bottom: 10px; font-weight: 600; }
        p { color: #94a3b8; font-size: 14px; line-height: 1.5; }
    </style>
    <script>
        setTimeout(function() { window.location.href = "{{ whatsapp_url }}"; }, 3500);
    </script>
</head>
<body>
    <div class="box">
        <div class="spinner"></div>
        <h1>Processando Solicitação</h1>
        <p>Encaminhando você para um consultor especialista da Converis via WhatsApp...</p>
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
    <title>CONVERIS - Painel de Gestão Corporativa</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background-color: #060a17; color: #f8fafc; margin: 0; padding: 0; }
        header { background: #0f172a; padding: 15px 30px; border-bottom: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px; }
        .logo-area { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; }
        .nav-tools { display: flex; gap: 8px; flex-wrap: wrap; }
        .container { max-width: 1200px; margin: 25px auto; padding: 0 15px; }
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .card-metric { background: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; }
        .card-metric h3 { margin: 0 0 8px 0; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        .card-metric .value { font-size: 24px; font-weight: 700; }
        .section-box { background: #0f172a; padding: 24px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #1e293b; }
        .section-box h3 { margin-top: 0; color: #f8fafc; font-size: 17px; font-weight: 600; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #1e293b; padding-bottom: 12px; }
        .lead-card { background: #020617; border: 1px solid #1e293b; padding: 16px; border-radius: 10px; margin-bottom: 12px; transition: border-color 0.2s; }
        .lead-card:hover { border-color: #334155; }
        .btn-whats { background: #10b981; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; }
        .btn-whats:hover { background: #059669; }
        .btn-action { background: #3b82f6; color: white; padding: 6px 12px; border-radius: 6px; border: none; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 10px; }
        .btn-action:hover { background: #2563eb; }
        .btn-tool { background: #1e293b; color: #f8fafc; padding: 8px 14px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 500; border: 1px solid #334155; display: inline-flex; align-items: center; gap: 6px; transition: background 0.2s; }
        .btn-tool:hover { background: #334155; }
        .badge-status { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
        .badge-prevenda { background: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.3); }
        .badge-vendas { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
        .badge-fechado { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-badge">C</div>
            <div>
                <h2 style="margin:0; font-size:16px; font-weight:600;">CONVERIS CRM</h2>
                <span style="font-size:11px; color: #94a3b8;">Gestão de Operações & Leads</span>
            </div>
        </div>
        <div class="nav-tools">
            <a href="/" class="btn-tool">🏠 Início</a>
            <a href="/catalogo" class="btn-tool">📦 Catálogo</a>
            <a href="/treinamento" class="btn-tool">🎓 Treinamento</a>
            <a href="/chat_equipa" class="btn-tool">💬 Chat Interno</a>
            <a href="/dre" class="btn-tool" style="border-color: #3b82f6; color: #60a5fa;">📊 DRE Corporativa</a>
        </div>
    </header>

    <div class="container">
        <div class="section-box">
            <h3>📈 Indicadores de Desempenho (Dashboard)</h3>
            <div class="grid-cards" style="margin-bottom:0;">
                <div class="card-metric">
                    <h3>⏳ Pré-Venda (Espera)</h3>
                    <div class="value" style="color: #facc15;">{{ total_prevenda }}</div>
                </div>
                <div class="card-metric">
                    <h3>🤝 Em Negociação (Vendas)</h3>
                    <div class="value" style="color: #60a5fa;">{{ total_vendas }}</div>
                </div>
                <div class="card-metric">
                    <h3>✅ Contratos Fechados</h3>
                    <div class="value" style="color: #34d399;">{{ total_fechados }}</div>
                </div>
                <div class="card-metric">
                    <h3>💰 Faturamento Bruto</h3>
                    <div class="value" style="color: #38bdf8;">R$ {{ "%.2f"|format(faturamento) }}</div>
                </div>
            </div>
        </div>

        <div class="section-box">
            <h3>📋 Pipeline de Atendimento</h3>
            
            <h4 style="color: #facc15; font-size: 13px; margin-top: 10px; text-transform: uppercase; letter-spacing: 0.5px;">⏳ Pré-Venda (Aguardando Contato Inicial)</h4>
            {% if leads_prevenda %}
                {% for lead in leads_prevenda %}
                <div class="lead-card" style="border-left: 3px solid #facc15;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 15px;">{{ lead['nome'] }}</strong>
                        <span class="badge-status badge-prevenda">{{ lead['status'] }}</span>
                    </div>
                    <div style="margin-top: 8px; color: #94a3b8; font-size: 13px; display: grid; gap: 3px;">
                        <span>📁 <strong>Serviço:</strong> {{ lead['servico'] }}</span>
                        <span>📞 <strong>Telefone:</strong> {{ lead['telefone'] }}</span>
                        <span>📝 <strong>Minuta:</strong> {{ lead['tipo_contrato'] }}</span>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;">
                        <a href="https://wa.me/{{ lead['telefone'] }}?text=Olá%20{{ lead['nome'] }},%20sou%20da%20Converis." target="_blank" class="btn-whats">📱 Abrir WhatsApp</a>
                        <a href="/atualizar_status/{{ lead['id'] }}/Vendas" class="btn-action">🤝 Mover para Vendas</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #64748b; font-size: 13px; font-style: italic; margin: 5px 0 15px 0;">Nenhum lead aguardando em pré-venda.</p>
            {% endif %}

            <h4 style="color: #60a5fa; font-size: 13px; margin-top: 25px; text-transform: uppercase; letter-spacing: 0.5px;">🤝 Vendas (Negociação em Andamento)</h4>
            {% if leads_vendas %}
                {% for lead in leads_vendas %}
                <div class="lead-card" style="border-left: 3px solid #60a5fa;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 15px;">{{ lead['nome'] }}</strong>
                        <span class="badge-status badge-vendas">{{ lead['status'] }}</span>
                    </div>
                    <div style="margin-top: 8px; color: #94a3b8; font-size: 13px; display: grid; gap: 3px;">
                        <span>📁 <strong>Serviço:</strong> {{ lead['servico'] }}</span>
                        <span>📞 <strong>Telefone:</strong> {{ lead['telefone'] }}</span>
                        <span style="color: #38bdf8; font-weight: 600;">💰 Valor Proposta: R$ {{ "%.2f"|format(lead['valor']) }}</span>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;">
                        <a href="https://wa.me/{{ lead['telefone'] }}" target="_blank" class="btn-whats">📱 WhatsApp</a>
                        <a href="/atualizar_status/{{ lead['id'] }}/Contrato_Fechado" class="btn-action" style="background: #10b981;">✅ Concluir / Fechar Contrato</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #64748b; font-size: 13px; font-style: italic; margin: 5px 0 15px 0;">Nenhum lead em fase de vendas ativa.</p>
            {% endif %}

            <h4 style="color: #34d399; font-size: 13px; margin-top: 25px; text-transform: uppercase; letter-spacing: 0.5px;">📄 Contratos Fechados (Concluídos)</h4>
            {% if contratos_lista %}
                {% for c in contratos_lista %}
                <div class="lead-card" style="border-left: 3px solid #10b981;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 15px;">{{ c['nome'] }}</strong>
                        <span class="badge-status badge-fechado">Fechado</span>
                    </div>
                    <div style="margin-top: 8px; color: #94a3b8; font-size: 13px; display: grid; gap: 3px;">
                        <span>📁 <strong>Serviço:</strong> {{ c['servico'] }}</span>
                        <span style="color: #34d399;">📄 <strong>Documento:</strong> {{ c['tipo_contrato'] }}</span>
                        <span style="color: #f8fafc; font-weight: 600;">Valor Fechado: R$ {{ "%.2f"|format(c['valor']) }}</span>
                    </div>
                    <div style="margin-top: 12px;">
                        <a href="/ver_contrato/{{ c['id'] }}" target="_blank" class="btn-action" style="background: #1e293b; border: 1px solid #334155;">👁️ Visualizar Contrato Emitido</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #64748b; font-size: 13px; font-style: italic; margin: 5px 0 0 0;">Nenhum contrato fechado registrado.</p>
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
        body { background-color: #060a17; color: #f8fafc; font-family: 'Segoe UI', system-ui, sans-serif; padding: 20px; }
        .box { background: #0f172a; padding: 30px; border-radius: 16px; border: 1px solid #1e293b; max-width: 850px; margin: 0 auto; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }
        h1 { color: #f8fafc; font-size: 20px; margin-top: 0; border-bottom: 1px solid #1e293b; padding-bottom: 15px; font-weight: 600; }
        .dre-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .dre-table th, .dre-table td { padding: 14px; text-align: left; border-bottom: 1px solid #1e293b; font-size: 14px; }
        .dre-table th { background-color: #020617; color: #38bdf8; font-weight: 600; }
        .row-total { font-weight: 600; background-color: #020617; color: #f8fafc; }
        .row-lucro { font-weight: 600; background-color: rgba(16, 185, 129, 0.1); color: #34d399; }
        .btn-voltar { background: #3b82f6; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 25px; font-size: 13px; }
        .btn-voltar:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="box">
        <h1>📊 DRE Corporativa (Demonstração do Resultado do Exercício)</h1>
        <p style="color: #94a3b8; font-size: 13px;">Relatório financeiro gerencial consolidado com base nos contratos fechados.</p>
        
        <table class="dre-table">
            <thead>
                <tr>
                    <th>Descrição do Indicador / Conta</th>
                    <th style="text-align: right;">Montante (R$)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>(+) Receita Bruta Operacional</strong></td>
                    <td style="text-align: right; color: #34d399; font-weight: 600;">R$ {{ "%.2f"|format(receita_bruta) }}</td>
                </tr>
                <tr>
                    <td>(-) Custos Operacionais Diretos Vinculados</td>
                    <td style="text-align: right; color: #f87171;">R$ {{ "%.2f"|format(custos_totais) }}</td>
                </tr>
                <tr class="row-total">
                    <td>(=) Resultado Bruto Operacional</td>
                    <td style="text-align: right;">R$ {{ "%.2f"|format(lucro_liquido) }}</td>
                </tr>
                <tr>
                    <td>(-) Provisão para Despesas Adm. e Tributárias (~10%)</td>
                    <td style="text-align: right; color: #f87171;">R$ {{ "%.2f"|format(receita_bruta * 0.10) }}</td>
                </tr>
                <tr class="row-lucro">
                    <td>(=) LUCRO LÍQUIDO OPERACIONAL CONSOLIDADO</td>
                    <td style="text-align: right;">R$ {{ "%.2f"|format(lucro_liquido - (receita_bruta * 0.10)) }}</td>
                </tr>
            </tbody>
        </table>

        <a href="/painel" class="btn-voltar">← Retornar ao CRM</a>
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
    <title>CONVERIS - Emissão de Instrumento Jurídico</title>
    <style>
        body { background-color: #060a17; color: #f8fafc; font-family: 'Segoe UI', system-ui, sans-serif; padding: 25px; display: flex; justify-content: center; }
        .contract-box { background: #0f172a; padding: 40px; border-radius: 16px; border: 1px solid #1e293b; width: 100%; max-width: 750px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }
        h1 { color: #f8fafc; font-size: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-top: 0; font-weight: 600; }
        p { line-height: 1.6; color: #cbd5e1; font-size: 14px; }
        .meta-info { background: #020617; padding: 15px; border-radius: 8px; border: 1px solid #1e293b; margin-bottom: 20px; }
        .btn-voltar { background: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 25px; font-size: 13px; }
        .btn-voltar:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="contract-box">
        <h1>📄 CONVERIS | {{ lead['tipo_contrato'] }}</h1>
        <div class="meta-info">
            <p style="margin: 0 0 5px 0;"><strong>Contratante (Cliente):</strong> {{ lead['nome'] }}</p>
            <p style="margin: 0 0 5px 0;"><strong>Telefone / WhatsApp:</strong> {{ lead['telefone'] }}</p>
            <p style="margin: 0;"><strong>Objeto Principal:</strong> {{ lead['servico'] }}</p>
        </div>
        
        <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO:</strong> O presente instrumento tem como objeto a prestação de serviços especializados de assessoria financeira e jurídica referentes a <em>{{ lead['servico'] }}</em>, prestados pela CONVERIS SOLUÇÕES FINANCEIRAS.</p>
        <p><strong>CLÁUSULA SEGUNDA - DOS HONORÁRIOS:</strong> O valor acordado para a execução dos serviços descritos é de R$ {{ "%.2f"|format(lead['valor']) }}, quitados conforme as condições comerciais pactuadas.</p>
        <p><strong>CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES:</strong> A CONVERIS compromete-se a empenhar todos os recursos técnicos e legais disponíveis visando o pleno atendimento das expectativas contratuais do cliente.</p>
        
        <div style="text-align: center; color: #34d399; font-weight: 600; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px; border-radius: 8px; margin-top: 25px; font-size: 13px;">
            ✅ Documento gerado digitalmente e autenticado pelo sistema corporativo Converis.
        </div>
        
        <a href="/painel" class="btn-voltar">← Retornar ao CRM</a>
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
        body { background-color: #060a17; color: #f8fafc; font-family: 'Segoe UI', system-ui, sans-serif; padding: 25px; }
        .box { background: #0f172a; padding: 30px; border-radius: 16px; border: 1px solid #1e293b; max-width: 850px; margin: 0 auto; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }
        h1 { color: #f8fafc; font-size: 20px; margin-top: 0; font-weight: 600; }
        .card-aula { background: #020617; border: 1px solid #1e293b; padding: 18px; border-radius: 10px; margin-bottom: 15px; }
        .btn-voltar { background: #3b82f6; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 15px; font-size: 13px; }
        .btn-voltar:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎓 Central de Treinamento & Scripts Comerciais</h1>
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 25px;">Diretrizes operacionais e abordagens padronizadas para maximização da conversão de leads.</p>
        
        <div class="card-aula">
            <h3 style="color: #38bdf8; margin-top: 0; font-size: 15px;">1. Abordagem Inicial - Lei do Superendividamento</h3>
            <p style="font-size: 13px; color: #cbd5e1; line-height: 1.5; margin-bottom: 0;">"Olá! Analisamos o seu perfil financeiro. O nosso foco principal é blindar o seu mínimo existencial e repactuar o conjunto das suas dívidas sob condições justas e sustentáveis..."</p>
        </div>

        <div class="card-aula">
            <h3 style="color: #38bdf8; margin-top: 0; font-size: 15px;">2. Tratamento de Objeções - Financiamentos em Atraso</h3>
            <p style="font-size: 13px; color: #cbd5e1; line-height: 1.5; margin-bottom: 0;">"A revisão contratual tem por objetivo recalcular encargos e taxas abusivas incidentes, viabilizando a regularização ou quitação viável do saldo devedor..."</p>
        </div>

        <a href="/painel" class="btn-voltar">← Retornar ao CRM</a>
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
    <title>CONVERIS - Chat Corporativo Interno</title>
    <style>
        body { background-color: #060a17; color: #f8fafc; font-family: 'Segoe UI', system-ui, sans-serif; padding: 25px; }
        .box { background: #0f172a; padding: 30px; border-radius: 16px; border: 1px solid #1e293b; max-width: 650px; margin: 0 auto; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }
        h1 { color: #f8fafc; font-size: 20px; margin-top: 0; font-weight: 600; }
        .chat-box { background: #020617; border: 1px solid #1e293b; padding: 15px; border-radius: 10px; height: 320px; overflow-y: auto; margin-bottom: 18px; display: flex; flex-direction: column; gap: 10px; }
        .msg { font-size: 13px; padding: 10px 12px; background: #0f172a; border-radius: 8px; border: 1px solid #1e293b; }
        .msg strong { color: #38bdf8; }
        .msg span { font-size: 11px; color: #64748b; float: right; }
        input, button { padding: 12px; border-radius: 8px; border: 1px solid #334155; }
        input { background: #020617; color: white; width: 72%; font-size: 14px; }
        input:focus { outline: none; border-color: #3b82f6; }
        button { background: #3b82f6; color: white; font-weight: 600; width: 25%; cursor: pointer; font-size: 14px; }
        button:hover { background: #2563eb; }
        .btn-voltar { background: #1e293b; color: #f8fafc; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: 500; display: inline-block; margin-top: 15px; font-size: 13px; border: 1px solid #334155; }
    </style>
</head>
<body>
    <div class="box">
        <h1>💬 Canal de Comunicação Interna (Equipe)</h1>
        <div class="chat-box">
            {% for msg in mensagens %}
            <div class="msg">
                <strong>{{ msg['autor'] }}:</strong> {{ msg['mensagem'] }} 
                <span>{{ msg['data_envio'] }}</span>
            </div>
            {% endfor %}
        </div>
        <form action="/enviar_chat" method="POST" style="display: flex; gap: 3%;">
            <input type="text" name="mensagem" placeholder="Digite uma mensagem para a equipe..." required autocomplete="off">
            <button type="submit">Enviar</button>
        </form>
        <a href="/painel" class="btn-voltar">← Retornar ao CRM</a>
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

@app.route('/
