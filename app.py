from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

leads = [
    {"id": 1, "nome": "Silvio Solimar silva da silva junior", "servico": "Financiamento/Veículos", "telefone": "51990113071", "valor": "54.00", "status": "Pré-Venda"}
]

mensagens_chat = [
    {"remetente": "Cliente (Silvio)", "texto": "Olá! Gostaria de informações sobre o contrato.", "hora": "22:30"},
    {"remetente": "Atendente (Aquiles)", "texto": "Olá Silvio! Vamos verificar o seu cadastro agora.", "hora": "22:31"}
]

catalogo_servicos = [
    {"titulo": "Lei do Superendividamento", "desc": "Como Renegociar Dívidas e Proteger o seu Mínimo Existencial. Renegociação judicial ou extrajudicial com foco em readequação e fim dos juros abusivos."},
    {"titulo": "Empréstimo Consignado do INSS", "desc": "Redução de até 50% na parcela. Análise do contrato, verificação de taxas, encargos e suporte especializado para aposentados e pensionistas."},
    {"titulo": "Dívida do Cartão de Crédito", "desc": "Saiu do controle e virou bola de neve? Análise especializada de juros altos, pagamento mínimo e renegociação para alcançar parcelas e custos mais justos."},
    {"titulo": "Parcelas Atrasadas (Financiamentos)", "desc": "Soluções judiciais e extrajudicial para contratos de veículos, consórcios e financiamentos com parcelas em atraso."}
]

modulos_treinamento = [
    {"titulo": "1. Abordagem Inicial e Empatia", "desc": "Entenda a dor do cliente (dívidas, superendividamento, juros abusivos). Ouça com atenção e demonstre que ele não está sozinho."},
    {"titulo": "2. Análise Contratual e Diagnóstico", "desc": "Instruções sobre como solicitar os extratos e contratos ao cliente para verificar taxas, encargos e margem consignável."},
    {"titulo": "3. Argumentação de Vendas e Fechamento", "desc": "Como apresentar os benefícios da negociação (proteção do mínimo existencial, redução de parcelas e segurança jurídica)."},
    {"titulo": "4. Utilização do CRM e Pós-Venda", "desc": "Como mover os leads pelo pipeline (Pré-Venda ➔ Vendas ➔ Contratos Fechados) e manter o acompanhamento ativo via WhatsApp."}
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS CRM</title>
    
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0b132b">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; margin: 0; padding: 0; }
        header { background: #0b132b; padding: 15px 20px; border-bottom: 2px solid #ffb703; display: flex; align-items: center; justify-content: space-between; }
        .logo-area { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background: #7209b7; color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; }
        .container { max-width: 1100px; margin: 15px auto; padding: 10px; }
        
        /* Menu superior completo */
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav-btn { background: #1c2541; color: white; border: none; padding: 10px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; font-size: 13px; border: 1px solid #3a506b; display: inline-flex; align-items: center; gap: 6px; }
        .nav-btn.active { background: #ffb703; color: #0b132b; border: none; }
        .nav-btn:hover { opacity: 0.9; }
        
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .card-metric { background: #1c2541; padding: 18px; border-radius: 8px; border: 1px solid #3a506b; }
        .card-metric h3 { margin: 0 0 8px 0; font-size: 11px; color: #8d99ae; letter-spacing: 0.5px; }
        .card-metric .value { font-size: 22px; font-weight: bold; }
        
        .section-box { background: #1c2541; padding: 18px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #3a506b; }
        .section-box h3 { margin-top: 0; color: #ffb703; font-size: 16px; display: flex; align-items: center; gap: 8px; }
        
        .lead-card { background: #0b132b; border: 1px solid #3a506b; padding: 14px; border-radius: 8px; margin-bottom: 12px; }
        .catalog-card { background: #0b132b; border: 1px solid #3a506b; padding: 14px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #ffb703; }
        .training-card { background: #0b132b; border: 1px solid #3a506b; padding: 14px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #2ec4b6; }
        
        .form-group { margin-bottom: 12px; }
        label { display: block; margin-bottom: 4px; font-size: 12px; color: #8d99ae; }
        input, select { width: 100%; padding: 10px; background: #0b132b; border: 1px solid #3a506b; color: white; border-radius: 6px; font-size: 14px; }
        
        button.submit-btn { background: #ffb703; color: #0b132b; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; font-size: 14px; }
        .btn-whats { background: #2ec4b6; color: white; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold; display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; }
        
        .chat-box { background: #0b132b; border: 1px solid #3a506b; border-radius: 8px; padding: 12px; height: 220px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
        .chat-msg { padding: 8px 12px; border-radius: 6px; max-width: 85%; font-size: 13px; }
        .msg-cliente { background: #28385e; align-self: flex-start; }
        .msg-atendente { background: #3a506b; align-self: flex-end; border-left: 3px solid #ffb703; }
        
        .dre-linha { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #28385e; font-size: 13px; }
        .dre-total { font-weight: bold; color: #4cc9f0; font-size: 15px; margin-top: 10px; }

        #pwa-install-banner { display: none; background: #7209b7; color: white; padding: 14px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: bold; justify-content: space-between; align-items: center; border: 1px solid #9d4edd; }
        #pwa-install-btn { background: #ffb703; color: #0b132b; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-badge">∞</div>
            <div>
                <h2 style="margin:0; font-size:18px;">CONVERIS CRM</h2>
                <span style="font-size:11px; color: #8d99ae;">ÁREA DA EQUIPE • AQUILES VENDAS</span>
            </div>
        </div>
    </header>

    <div class="container">
        <!-- Banner PWA -->
        <div id="pwa-install-banner">
            <span>📲 Deseja instalar o Converis CRM como Aplicativo?</span>
            <button id="pwa-install-btn">Instalar App</button>
        </div>

        <!-- Menu de Navegação Superior Completo -->
        <div class="nav-tabs">
            <a href="/" class="nav-btn active">🏠 Início</a>
            <a href="#leads-section" class="nav-btn" style="background: #ffb703; color: #0b132b;">📋 Gestão de Leads</a>
            <a href="#catalogo-section" class="nav-btn" style="background: #3a506b;">📦 Catálogo</a>
            <a href="#treinamento-section" class="nav-btn" style="background: #4cc9f0; color: #0b132b;">🎓 Treinamento</a>
            <a href="#leads-section" class="nav-btn" style="background: #e76f51;">⏳ Pré-Venda</a>
            <a href="#leads-section" class="nav-btn" style="background: #2a9d8f;">🤝 Vendas</a>
            <a href="#leads-section" class="nav-btn" style="background: #264653;">✅ Concluídas</a>
            <a href="#leads-section" class="nav-btn" style="background: #e9c46a; color: #0b132b;">📄 Contratos</a>
            <a href="#chat-section" class="nav-btn" style="background: #28385e;">💬 Chat ao Vivo</a>
            <a href="#dre-section" class="nav-btn" style="background: #7209b7;">📊 DRE Corporativa</a>
        </div>

        <!-- Cards de Caixa -->
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
                <h3>TOTAL INADIMPLENTE / DEVENDO</h3>
                <div class="value" style="color: #e71d36;">R$ 0,00</div>
            </div>
        </div>

        <!-- Catálogo de Serviços -->
        <div class="section-box" id="catalogo-section">
            <h3>📦 Catálogo de Serviços - Converis Soluções Financeiras</h3>
            <p style="font-size: 13px; color: #8d99ae; margin-top:0;">Soluções judiciais e extrajudiciais para renegociação de dívidas e proteção do património.</p>
            {% for serv in catalogo_servicos %}
            <div class="catalog-card">
                <strong>{{ serv.titulo }}</strong>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #d8dee9;">{{ serv.desc }}</p>
                <a href="https://wa.me/5551999797731?text=Olá,%20gostaria%20de%20saber%20mais%20sobre%20o%20serviço:%20{{ serv.titulo }}" target="_blank" class="btn-whats">📱 Consultar via Whats</a>
            </div>
            {% endfor %}
        </div>

        <!-- Módulos de Treinamento -->
        <div class="section-box" id="treinamento-section">
            <h3>🎓 Treinamento da Equipe & Orientações de Vendas</h3>
            <p style="font-size: 13px; color: #8d99ae; margin-top:0;">Orientações práticas para o atendimento de excelência da Aquiles Vendas.</p>
            {% for mod in modulos_treinamento %}
            <div class="training-card">
                <strong>{{ mod.titulo }}</strong>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #d8dee9;">{{ mod.desc }}</p>
            </div>
            {% endfor %}
        </div>

        <!-- Chat de Atendimento -->
        <div class="section-box" id="chat-section">
            <h3>💬 Chat de Atendimento ao Cliente</h3>
            <div class="chat-box">
                {% for msg in mensagens_chat %}
                    {% if "Cliente" in msg.remetente %}
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
                <input type="text" name="texto_mensagem" required placeholder="Digite a mensagem para o cliente..." style="flex: 1;">
                <button type="submit" style="background: #2ec4b6; color: white; border: none; padding: 0 16px; border-radius: 6px; font-weight: bold; cursor: pointer;">Enviar</button>
            </form>
        </div>

        <!-- Formulário de Cadastro -->
        <div class="section-box">
            <h3>➕ Cadastrar Novo Lead Manualmente</h3>
            <form action="/add" method="POST">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-group">
                        <label>Nome do Cliente *</label>
                        <input type="text" name="nome" required placeholder="Nome do Cliente">
                    </div>
                    <div class="form-group">
                        <label>Serviço (ex: INSS, Cartão)</label>
                        <input type="text" name="servico" required placeholder="Ex: Financiamento/Veículos">
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-group">
                        <label>WhatsApp</label>
                        <input type="text" name="telefone" required placeholder="51999999999">
                    </div>
                    <div class="form-group">
                        <label>Valor da Dívida (R$)</label>
                        <input type="text" name="valor" required placeholder="54.00">
                    </div>
                </div>
                <div class="form-group">
                    <label>Etapa Inicial</label>
                    <select name="status">
                        <option value="Pré-Venda">⏳ Pré-Venda (Espera)</option>
                        <option value="Em Atendimento">🤝 Vendas (Em Atendimento)</option>
                        <option value="Concluída">✅ Concluída</option>
                        <option value="Contrato Fechado">📄 Contrato Fechado</option>
                    </select>
                </div>
                <button type="submit" class="submit-btn">Adicionar Card</button>
            </form>
        </div>

        <!-- Pipeline de Leads e Atendimento -->
        <div class="section-box" id="leads-section">
            <h3>🔵 Pipeline de Atendimento & Gestão de Clientes</h3>
            {% for lead in leads %}
            <div class="lead-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{{ lead.nome }}</strong>
                    <span style="background: #ffb703; color: #0b132b; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{{ lead.status }}</span>
                </div>
                <span style="color: #8d99ae; font-size: 12px;">📁 Serviço: {{ lead.servico }}</span><br>
                <span style="color: #8d99ae; font-size: 12px;">📞 Tel: {{ lead.telefone }}</span>
                <div style="color: #2ec4b6; font-weight: bold; margin-top: 4px;">R$ {{ lead.valor }}</div>
                <a href="https://wa.me/{{ lead.telefone }}?text=Olá%20{{ lead.nome }},%20estamos%20a%20entrar%20em%20contacto." target="_blank" class="btn-whats">📱 Falar no Whats</a>
            </div>
            {% endfor %}
        </div>

        <!-- DRE Corporativa Detalhada -->
        <div class="section-box" id="dre-section">
            <h3>📊 DRE Corporativa Detalhada</h3>
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
            <div class="dre-linha">
                <span>(-) Custos e Despesas Operacionais</span>
                <span style="color: #e71d36;">R$ 0,00</span>
            </div>
            <div class="dre-total">
                (=) LUCRO LÍQUIDO DO EXERCÍCIO: <span style="color: #2ec4b6;">R$ 49,68</span>
            </div>
        </div>
    </div>

    <!-- Script de Instalação PWA -->
    <script>
        let deferredPrompt;
        const banner = document.getElementById('pwa-install-banner');
        const installBtn = document.getElementById('pwa-install-btn');

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            banner.style.display = 'flex';
        });

        installBtn.addEventListener('click', () => {
            banner.style.display = 'none';
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    deferredPrompt = null;
                });
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, leads=leads, mensagens_chat=mensagens_chat, catalogo_servicos=catalogo_servicos, modulos_treinamento=modulos_treinamento)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/add', methods=['POST'])
def add_lead():
    novo_id = len(leads) + 1
    nome = request.form.get('nome')
    servico = request.form.get('servico')
    telefone = request.form.get('telefone')
    valor = request.form.get('valor')
    status = request.form.get('status') or 'Pré-Venda'
    leads.append({"id": novo_id, "nome": nome, "servico": servico, "telefone": telefone, "valor": valor, "status": status})
    return redirect(url_for('index') + '#leads-section')

@app.route('/enviar_chat', methods=['POST'])
def enviar_chat():
    texto = request.form.get('texto_mensagem')
    if texto:
        mensagens_chat.append({"remetente": "Atendente (Aquiles)", "texto": texto})
    return redirect(url_for('index') + '#chat-section')

if __name__ == '__main__':
    app.run()
