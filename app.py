from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, session
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey_converis'

# Dados globais do CRM sincronizados
leads = [
    {"id": 1, "nome": "Silvio Solimar silva da silva junior", "servico": "Financiamento/Veículos", "telefone": "51990113071", "valor": "54.00", "status": "Pré-Venda"}
]

mensagens_chat = [
    {"remetente": "Cliente", "texto": "Olá! Gostaria de informações sobre o contrato.", "hora": "22:30"},
    {"remetente": "Atendente (Aquiles)", "texto": "Olá Silvio! Vamos verificar o seu cadastro agora.", "hora": "22:31"}
]

catalogo_servicos = [
    {"titulo": "Lei do Superendividamento", "desc": "Como Renegociar Dívidas e Proteger o seu Mínimo Existencial. Foco em readequação e fim dos juros abusivos."},
    {"titulo": "Empréstimo Consignado do INSS", "desc": "Redução de até 50% na parcela com análise completa de contratos e taxas para aposentados e pensionistas."},
    {"titulo": "Dívida do Cartão de Crédito", "desc": "Soluções para juros altos, pagamento mínimo e renegociação de faturas que viraram bola de neve."},
    {"titulo": "Parcelas Atrasadas (Financiamentos)", "desc": "Soluções judiciais e extrajudiciais para veículos, consórcios e contratos com atraso."}
]

modulos_treinamento = [
    {"titulo": "1. Abordagem Inicial e Empatia", "desc": "Entenda a dor do cliente (dívidas, superendividamento, juros abusivos) e demonstre segurança."},
    {"titulo": "2. Análise Contratual e Diagnóstico", "desc": "Instruções sobre como solicitar os extratos e contratos ao cliente para verificar taxas e margem."},
    {"titulo": "3. Argumentação de Vendas e Fechamento", "desc": "Como apresentar os benefícios da negociação e fechar o contrato com o cliente."},
    {"titulo": "4. Utilização do CRM e Pós-Venda", "desc": "Como mover os leads pelo pipeline e manter o acompanhamento ativo via WhatsApp."}
]

# ETAPA 1 DO CLIENTE: Dados Iniciais
FORM_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Soluções Financeiras</title>
    <meta name="theme-color" content="#0b132b">
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
        <p>Preencha os seus dados para iniciar o atendimento personalizado.</p>
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

# ETAPA 2 DO CLIENTE: Escolha do Serviço (Catálogo)
SERVICE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Catálogo de Serviços</title>
    <meta name="theme-color" content="#0b132b">
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

# ETAPA 3 DO CLIENTE: Redirecionamento
REDIRECT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecionando...</title>
    <meta name="theme-color" content="#0b132b">
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
        setTimeout(function() {
            window.location.href = "{{ whatsapp_url }}";
        }, 3500);
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

# PAINEL INTERNO DA EQUIPA (Com TODOS os botões e secções solicitadas)
PANEL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS - Painel da Equipa</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0b132b">
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; margin: 0; padding: 0; }
        header { background: #0b132b; padding: 15px 20px; border-bottom: 2px solid #ffb703; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
        .logo-area { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background: #7209b7; color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; }
        .container { max-width: 1100px; margin: 15px auto; padding: 10px; }
        
        .nav-tabs { display: flex; gap: 6px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav-btn { background: #1c2541; color: white; border: 1px solid #3a506b; padding: 8px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; }
        .nav-btn.active { background: #ffb703; color: #0b132b; border: none; }
        
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .card-metric { background: #1c2541; padding: 16px; border-radius: 8px; border: 1px solid #3a506b; }
        .card-metric h3 { margin: 0 0 8px 0; font-size: 11px; color: #8d99ae; }
        .card-metric .value { font-size: 20px; font-weight: bold; }
        
        .section-box { background: #1c2541; padding: 18px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #3a506b; }
        .section-box h3 { margin-top: 0; color: #ffb703; font-size: 16px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #3a506b; padding-bottom: 8px; }
        
        .lead-card { background: #0b132b; border: 1px solid #3a506b; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
        .training-card { background: #0b132b; border: 1px solid #3a506b; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #2ec4b6; }
        
        .btn-whats { background: #2ec4b6; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; }
        
        .chat-box { background: #0b132b; border: 1px solid #3a506b; border-radius: 8px; padding: 12px; height: 220px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
        .chat-msg { padding: 8px 12px; border-radius: 6px; max-width: 85%; font-size: 13px; }
        .msg-cliente { background: #28385e; align-self: flex-start; }
        .msg-atendente { background: #3a506b; align-self: flex-end; border-left: 3px solid #ffb703; }
        
        .dre-linha { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #28385e; font-size: 13px; }
        .dre-total { font-weight: bold; color: #4cc9f0; font-size: 15px; margin-top: 10px; }
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
        <a href="/" class="nav-btn" style="background: #1c2541; color: #2ec4b6; border-color: #2ec4b6;">🌐 Ver Início do Cliente</a>
    </header>

    <div class="container">
        <!-- TODOS OS BOTÕES DE NAVEGAÇÃO PEDIDOS -->
        <div class="nav-tabs">
            <a href="/painel" class="nav-btn active">🏠 Início</a>
            <a href="#leads-section" class="nav-btn" style="background: #ffb703; color: #0b132b;">📋 Gestão de Leads</a>
            <a href="#dashboard-section" class="nav-btn" style="background: #3a506b;">🏠 Dashboard</a>
            <a href="#catalogo-section" class="nav-btn" style="background: #7209b7;">📦 Catálogo</a>
            <a href="#treinamento-section" class="nav-btn" style="background: #4cc9f0; color: #0b132b;">🎓 Treinamento</a>
            <a href="#chat-section" class="nav-btn" style="background: #28385e;">💬 Chat ao Vivo</a>
            <a href="#dre-section" class="nav-btn" style="background: #4361ee;">📊 DRE Corporativa</a>
        </div>

        <!-- Dashboard / Métricas de Caixa -->
        <div class="section-box" id="dashboard-section">
            <h3>🏠 Dashboard & Métricas Financeiras</h3>
            <div class="grid-cards" style="margin-bottom:0;">
                <div class="card-metric">
                    <h3>JÁ RECEBIDO (CAIXA)</h3>
                    <div class="value" style="color: #2ec4b6;">R$ 0,00</div>
                </div>
                <div class="card-metric">
                    <h3>A RECEBER (FALTA PAGAR)</h3>
                    <div class="value" style="color: #ffb703;">R$ 54,00</div>
                </div>
                <div class="card-metric">
                    <h3>TOTAL INADIMPLENTE / DEVENDO</h3>
                    <div class="value" style="color: #e71d36;">R$ 0,00</div>
                </div>
            </div>
        </div>

        <!-- Gestão de Leads / Funil (Pré-Venda, Vendas, Concluídas, Contratos Fechados) -->
        <div class="section-box" id="leads-section">
            <h3>📋 Gestão de Leads & Funil de Atendimento</h3>
            <div style="display: flex; gap: 8px; margin-bottom: 15px; flex-wrap: wrap;">
                <span class="nav-btn" style="background: #3a506b; font-size: 11px;">⏳ Pré-Venda (Espera)</span>
                <span class="nav-btn" style="background: #ffb703; color: #0b132b; font-size: 11px;">🤝 Vendas (Em Atendimento)</span>
                <span class="nav-btn" style="background: #2ec4b6; color: white; font-size: 11px;">✅ Concluídas</span>
                <span class="nav-btn" style="background: #7209b7; font-size: 11px;">📄 Contratos Fechados</span>
            </div>
            
            {% for lead in leads %}
            <div class="lead-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{{ lead.nome }}</strong>
                    <span style="background: #ffb703; color: #0b132b; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{{ lead.status }}</span>
                </div>
                <span style="color: #8d99ae; font-size: 12px;">📁 Serviço: {{ lead.servico }}</span><br>
                <span style="color: #8d99ae; font-size: 12px;">📞 Tel: {{ lead.telefone }}</span>
                <div style="color: #2ec4b6; font-weight: bold; margin-top: 4px;">R$ {{ lead.valor }}</div>
                <a href="https://wa.me/{{ lead.telefone }}?text=Olá%20{{ lead.nome }},%20estamos%20a%20entrar%20em%20contacto%20sobre%20o%20seu%20atendimento." target="_blank" class="btn-whats">📱 Falar no Whats</a>
            </div>
            {% endfor %}
        </div>

        <!-- Catálogo Interno -->
        <div class="section-box" id="catalogo-section">
            <h3>📦 Catálogo de Serviços Disponíveis</h3>
            {% for serv in catalogo_servicos %}
            <div class="lead-card">
                <strong>{{ serv.titulo }}</strong>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #d8dee9;">{{ serv.desc }}</p>
            </div>
            {% endfor %}
        </div>

        <!-- Chat ao Vivo -->
        <div class="section-box" id="chat-section">
            <h3>💬 Chat ao Vivo com Clientes</h3>
            <div class="chat-box">
                {% for msg in mensagens_chat %}
                    {% if "Atendente" not in msg.remetente %}
                    <div class="chat-msg msg-cliente">
                        <strong>{{ msg.remetente }}:</strong> {{ msg.texto }}
                    </div>
                    {% else %}
                    <div class="chat-msg msg-atendente">
                        <strong>{{ msg.remetente }}:</strong> {{ msg.texto }}
                    </div>
                    {% endif %}
                {% endfor %}
            </div>
            <form action="/enviar_chat" method="POST" style="display: flex; gap: 8px;">
                <input type="text" name="texto_mensagem" required placeholder="Digite a resposta para o cliente..." style="flex: 1; padding: 10px; background: #0b132b; border: 1px solid #3a506b; color: white; border-radius: 6px; font-size: 14px;">
                <button type="submit" style="background: #2ec4b6; color: white; border: none; padding: 0 16px; border-radius: 6px; font-weight: bold; cursor: pointer;">Enviar</button>
            </form>
        </div>

        <!-- Treinamento -->
        <div class="section-box" id="treinamento-section">
            <h3>🎓 Treinamento da Equipa</h3>
            {% for mod in modulos_treinamento %}
            <div class="training-card">
                <strong>{{ mod.titulo }}</strong>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #d8dee9;">{{ mod.desc }}</p>
            </div>
            {% endfor %}
        </div>

        <!-- DRE Corporativa -->
        <div class="section-box" id="dre-section">
            <h3>📊 DRE Corporativa</h3>
            <div class="dre-linha">
                <span>(+) Receita Total Contratada</span>
                <span style="color: #2ec4b6;">R$ 54,00</span>
            </div>
            <div class="dre-linha">
                <span>(-) Deduções e Impostos (~8%)</span>
                <span style="color: #e71d36;">R$ 4,32</span>
            </div>
            <div class="dre-linha" style="font-weight: bold; background: #0b132b; padding: 6px;">
                <span>(=) Receita Líquida</span>
                <span>R$ 49,68</span>
            </div>
            <div class="dre-total">
                (=) LUCRO LÍQUIDO: <span style="color: #2ec4b6;">R$ 49,68</span>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Rotas da Aplicação
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
    
    if nome and telefone:
        # Sincroniza e adiciona automaticamente como lead na Pré-Venda
        leads.append({"id": len(leads) + 1, "nome": nome, "servico": servico, "telefone": telefone, "valor": "0.00", "status": "Pré-Venda"})
        mensagens_chat.append({"remetente": f"Cliente ({nome})", "texto": f"Interesse em: {servico}", "hora": "Agora"})

    mensagem = f"Olá, meu nome é {nome}. Gostaria de atendimento sobre o serviço: {servico}."
    whatsapp_url = f"https://wa.me/5551999797731?text={mensagem}"
    
    return render_template_string(REDIRECT_TEMPLATE, whatsapp_url=whatsapp_url)

@app.route('/painel')
def painel_equipe():
    return render_template_string(PANEL_TEMPLATE, leads=leads, mensagens_chat=mensagens_chat, modulos_treinamento=modulos_treinamento)

@app.route('/enviar_chat', methods=['POST'])
def enviar_chat():
    texto = request.form.get('texto_mensagem')
    if texto:
        mensagens_chat.append({"remetente": "Atendente (Aquiles)", "texto": texto, "hora": "Agora"})
    return redirect(url_for('painel_equipe') + '#chat-section')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

if __name__ == '__main__':
    app.run(port=5000)
