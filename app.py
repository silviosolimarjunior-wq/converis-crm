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

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            servico TEXT,
            telefone TEXT,
            valor TEXT,
            status TEXT,
            tipo_contrato TEXT
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
        cursor.execute("INSERT INTO leads (nome, servico, telefone, valor, status, tipo_contrato) VALUES (?, ?, ?, ?, ?, ?)",
                       ("Silvio Solimar silva da silva junior", "Financiamento/Veículos", "51990113071", "54.00", "Pré-Venda", "Contrato de Defesa de Financiamento"))
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
        <h1>CONVERIS</h1>
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
            <button type="submit">Avançar para Serviços</button>
        </form>
        <a href="/painel" class="team-link">🔒 Área da Equipa (CRM)</a>
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
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .card-metric { background: #1c2541; padding: 16px; border-radius: 8px; border: 1px solid #3a506b; }
        .card-metric h3 { margin: 0 0 8px 0; font-size: 11px; color: #8d99ae; }
        .card-metric .value { font-size: 20px; font-weight: bold; }
        .section-box { background: #1c2541; padding: 18px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #3a506b; }
        .section-box h3 { margin-top: 0; color: #ffb703; font-size: 16px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #3a506b; padding-bottom: 8px; }
        .lead-card { background: #0b132b; border: 1px solid #3a506b; padding: 12px; border-radius: 8px; margin-bottom: 12px; }
        .btn-whats { background: #2ec4b6; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; }
        .btn-action { background: #ffb703; color: #0b132b; padding: 6px 12px; border-radius: 4px; border: none; font-size: 12px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 5px; }
        .btn-tool { background: #3a506b; color: #ffffff; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; border: 1px solid #ffb703; display: inline-flex; align-items: center; gap: 4px; }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-badge">∞</div>
            <div>
                <h2 style="margin:0; font-size:18px;">CONVERIS CRM</h2>
                <span style="font-size:11px; color: #8d99ae;">PAINEL INTERNO • AQUILES VENDAS</span>
            </div>
        </div>
        <div class="nav-tools">
            <a href="/treinamento" class="btn-tool">🎓 Treinamento</a>
            <a href="/leilao_led" class="btn-tool">🚨 Leilão (LED)</a>
            <a href="/chat_equipa" class="btn-tool">💬 Chat Interno</a>
            <a href="/" class="btn-action" style="background: #1c2541; color: #2ec4b6; border: 1px solid #2ec4b6;">🌐 Início Cliente</a>
        </div>
    </header>

    <div class="container">
        <div class="section-box">
            <h3>🏠 Dashboard & Métricas Financeiras</h3>
            <div class="grid-cards" style="margin-bottom:0;">
                <div class="card-metric">
                    <h3>JÁ RECEBIDO (CAIXA)</h3>
                    <div class="value" style="color: #2ec4b6;">R$ {{ total_recebido }}</div>
                </div>
                <div class="card-metric">
                    <h3>A RECEBER (FALTA PAGAR)</h3>
                    <div class="value" style="color: #ffb703;">R$ {{ total_areceber }}</div>
                </div>
                <div class="card-metric">
                    <h3>CONTRATOS FECHADOS</h3>
                    <div class="value" style="color: #7209b7;">{{ total_fechados }}</div>
                </div>
            </div>
        </div>

        <div class="section-box">
            <h3>📋 Gestão de Leads & Funil de Atendimento</h3>
            <h4 style="color: #8d99ae; font-size: 13px; margin-bottom: 8px;">Leads em Atendimento:</h4>
            {% if leads %}
                {% for lead in leads %}
                <div class="lead-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{{ lead[1] }}</strong>
                        <span style="background: #ffb703; color: #0b132b; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{{ lead[5] }}</span>
                    </div>
                    <span style="color: #8d99ae; font-size: 12px;">📁 Serviço: {{ lead[2] }}</span><br>
                    <span style="color: #8d99ae; font-size: 12px;">📞 Tel: {{ lead[3] }}</span><br>
                    <span style="color: #4cc9f0; font-size: 12px; font-weight: bold;">📝 Contrato Sugerido: {{ lead[6] }}</span>
                    <div style="color: #2ec4b6; font-weight: bold; margin-top: 4px;">R$ {{ lead[4] }}</div>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px;">
                        <a href="https://wa.me/{{ lead[3] }}?text=Olá%20{{ lead[1] }},%20estamos%20a%20entrar%20em%20contacto." target="_blank" class="btn-whats">📱 WhatsApp</a>
                        <a href="/atualizar_status/{{ lead[0] }}/Vendas" class="btn-action" style="background: #3a506b; color: white;">Mover p/ Vendas</a>
                        <a href="/atualizar_status/{{ lead[0] }}/Contrato_Fechado" class="btn-action">📄 Fechar Contrato</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #8d99ae; font-size: 13px; font-style: italic;">Nenhum lead ativo no momento.</p>
            {% endif %}

            <h4 style="color: #ffb703; font-size: 13px; margin-top: 25px; margin-bottom: 8px; border-top: 1px solid #3a506b; padding-top: 15px;">📄 Contratos Fechados / Emitidos:</h4>
            {% if contratos_lista %}
                {% for c in contratos_lista %}
                <div class="lead-card" style="border-left: 4px solid #7209b7;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{{ c[1] }}</strong>
                        <span style="background: #7209b7; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">Fechado</span>
                    </div>
                    <span style="color: #8d99ae; font-size: 12px;">📁 Serviço: {{ c[2] }}</span><br>
                    <span style="color: #4cc9f0; font-size: 12px; font-weight: bold;">📄 Documento: {{ c[6] }}</span>
                    <div style="margin-top: 10px;">
                        <a href="/ver_contrato/{{ c[0] }}" target="_blank" class="btn-action" style="background: #2ec4b6; color: #0b132b;">👁️ Ver Contrato em Texto</a>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #8d99ae; font-size: 13px; font-style: italic;">Ainda nenhum contrato fechado.</p>
            {% endif %}
        </div>
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
        <h1>📄 {{ lead[6] }}</h1>
        <p><strong>Contratante (Cliente):</strong> {{ lead[1] }}</p>
        <p><strong>Telefone / WhatsApp:</strong> {{ lead[3] }}</p>
        <p><strong>Serviço Contratado:</strong> {{ lead[2] }}</p>
        <hr style="border-color: #3a506b; margin: 20px 0;">
        <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO:</strong> O presente instrumento tem como objeto a prestação de serviços especializados de assessoria e consultoria financeira referentes ao serviço de <em>{{ lead[2] }}</em>, prestados pela CONVERIS SOLUÇÕES FINANCEIRAS.</p>
        <p><strong>CLÁUSULA SEGUNDA - DOS HONORÁRIOS:</strong> O valor acordado para a prestação dos serviços acima descritos é de R$ {{ lead[4] }}, pagos conforme as condições alinhadas no atendimento via canais oficiais.</p>
        <p><strong>CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES:</strong> A CONVERIS compromete-se a envidar todos os esforços técnicos e legais para o sucesso da demanda apresentada pelo contratante.</p>
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
        <h1>🎓 Módulos de Treinamento e Scripts</h1>
        <p style="color: #8d99ae;">Instruções e abordagens comerciais para a equipa da Converis.</p>
        
        <div class="card-aula">
            <h3 style="color: #2ec4b6; margin-top: 0;">1. Abordagem Inicial - Superendividamento</h3>
            <p style="font-size: 13px; color: #d8dee9;">"Olá, tudo bem? Notei o seu contacto sobre a repactuação de dívidas. O nosso objetivo é proteger o seu mínimo existencial e renegociar os valores em condições justas..."</p>
        </div>

        <div class="card-aula">
            <h3 style="color: #2ec4b6; margin-top: 0;">2. Quebra de Objeções em Consignados</h3>
            <p style="font-size: 13px; color: #d8dee9;">"Compreendo a dúvida sobre o desconto em folha. A nossa revisão foca em identificar cobranças indevidas de juros e taxas abusivas no contrato..."</p>
        </div>

        <a href="/painel" class="btn-voltar">← Voltar ao CRM</a>
    </div>
</body>
</html>
'''

LEILAO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Leilão de Leads (LED)</title>
    <style>
        body { background-color: #0b132b; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }
        .box { background: #1c2541; padding: 25px; border-radius: 12px; border: 1px solid #3a506b; max-width: 800px; margin: 0 auto; }
        h1 { color: #ffb703; font-size: 22px; margin-top: 0; }
        .card-led { background: #0b132b; border: 1px solid #3a506b; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #ffb703; }
        .btn-pegar { background: #2ec4b6; color: #0b132b; padding: 6px 12px; border-radius: 4px; font-weight: bold; text-decoration: none; font-size: 12px; display: inline-block; margin-top: 8px; }
        .btn-voltar { background: #ffb703; color: #0b132b; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🚨 Leilão de Leads (Disponíveis para Assumir)</h1>
        <p style="color: #8d99ae;">Leads sem consultor atribuído ou disponíveis para novo contacto rápido.</p>

        {% if leads_livres %}
            {% for lead in leads_livres %}
            <div class="card-led">
                <strong>{{ lead[1] }}</strong> - <span style="color:#ffb703;">{{ lead[2] }}</span><br>
                <span style="font-size: 12px; color: #8d99ae;">Telefone: {{ lead[3] }}</span><br>
                <a href="/painel" class="btn-pegar">⚡ Assumir Atendimento</a>
            </div>
            {% endfor %}
        {% else %}
            <p style="color: #8d99ae; font-style: italic;">Nenhum lead em leilão no momento.</p>
        {% endif %}

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
    <title>CONVERIS - Chat Interno</title>
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
        <h1>💬 Chat Interno da Equipa</h1>
        <div class="chat-box">
            {% for msg in mensagens %}
            <div class="msg">
                <strong>{{ msg[1] }}:</strong> {{ msg[2] }} <span>({{ msg[3] }})</span>
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

@app.route('/etapa2', methods=['POST'])
def etapa2():
    session['nome'] = request.form.get('nome')
    session['telefone'] = request.form.get('telefone')
    return render_template_string(SERVICE_TEMPLATE, servicos=catalogo_servicos)

@app.route('/etapa3', methods=['POST'])
def etapa3():
    servico = request.form.get('servico')
    nome = session.get('nome')
    telefone = session.get('telefone')
    tipo_contrato = CONTRATOS_POR_SERVICO.get(servico, "Contrato Geral de Prestação de Serviços")
    if nome and telefone:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO leads (nome, servico, telefone, valor, status, tipo_contrato) VALUES (?, ?, ?, ?, ?, ?)",
                           (nome, servico, telefone, "54.00", "Pré-Venda", tipo_contrato))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Erro ao inserir lead:", e)

    mensagem = f"Olá, meu nome é {nome}. Gostaria de atendimento sobre o serviço: {servico}."
    whatsapp_url = f"https://wa.me/5551999797731?text={mensagem}"
    return render_template_string(REDIRECT_TEMPLATE, whatsapp_url=whatsapp_url)

@app.route('/painel')
def painel_equipe():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE status != 'Contrato Fechado'")
        leads = cursor.fetchall()
        cursor.execute("SELECT * FROM leads WHERE status = 'Contrato Fechado'")
        contratos_lista = cursor.fetchall()
        conn.close()
    except Exception:
        leads = []
        contratos_lista = []
    
    total_areceber = "54.00" if leads else "0,00"
    total_recebido = "0,00"
    total_fechados = len(contratos_lista)
    return render_template_string(PANEL_TEMPLATE, leads=leads, contratos_lista=contratos_lista, 
                                  total_areceber=total_areceber, total_recebido=total_recebido, 
                                  total_fechados=total_fechados)

@app.route('/treinamento')
def treinamento():
    return render_template_string(TREINAMENTO_TEMPLATE)

@app.route('/leilao_led')
def leilao_led():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE status = 'Pré-Venda'")
        leads_livres = cursor.fetchall()
        conn.close()
    except Exception:
        leads_livres = []
    return render_template_string(LEILAO_TEMPLATE, leads_livres=leads_livres)

@app.route('/chat_equipa')
def chat_equipa():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_mensagens ORDER BY id DESC LIMIT 20")
        mensagens = cursor.fetchall()
        conn.close()
    except Exception:
        mensagens = []
    return render_template_string(CHAT_TEMPLATE, mensagens=reversed(mensagens))

@app.route('/enviar_chat', methods=['POST'])
def enviar_chat():
    msg = request.form.get('mensagem')
    if msg:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chat_mensagens (autor, mensagem) VALUES (?, ?)", ("Aquiles", msg))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Erro no chat:", e)
    return redirect(url_for('chat_equipa'))

@app.route('/atualizar_status/<int:lead_id>/<path:novo_status>')
def atualizar_status(lead_id, novo_status):
    try:
        status_formatado = novo_status.replace('_', ' ')
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (status_formatado, lead_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Erro ao atualizar status:", e)
    return redirect(url_for('painel_equipe'))

@app.route('/ver_contrato/<int:lead_id>')
def ver_contrato(lead_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        lead = cursor.fetchone()
        conn.close()
        if lead:
            return render_template_string(CONTRATO_VIEW_TEMPLATE, lead=lead)
    except Exception as e:
        print("Erro ao ver contrato:", e)
    return "Contrato não encontrado", 404

if __name__ == '__main__':
    app.run(port=5000)
