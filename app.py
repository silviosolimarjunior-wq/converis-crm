from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Converis CRM - Martik</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7f6;
                margin: 0;
                padding: 0;
            }
            header {
                background: linear-gradient(135deg, #1e3c72, #2a5298);
                color: white;
                padding: 20px 40px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .logo-area {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .logo-icon {
                background: #ff6b6b;
                color: white;
                font-weight: bold;
                font-size: 24px;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            .brand-title h1 {
                margin: 0;
                font-size: 22px;
                letter-spacing: 0.5px;
            }
            .brand-title p {
                margin: 0;
                font-size: 13px;
                color: #dcdcdc;
            }
            .container {
                max-width: 1000px;
                margin: 40px auto;
                padding: 30px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }
            .card {
                background: #f8f9fa;
                border-left: 5px solid #2a5298;
                padding: 20px;
                border-radius: 6px;
                margin-top: 20px;
            }
        </style>
        <!-- Meta Pixel Code -->
        <script>
        !function(f,b,e,v,n,t,s)
        {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};
        if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
        n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t,s)}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
        fbq('init', '123456789012345');
        fbq('track', 'PageView');
        </script>
        <noscript><img height="1" width="1" style="display:none"
        src="https://www.facebook.com/tr?id=123456789012345&ev=PageView&noscript=1"
        /></noscript>
        <!-- End Meta Pixel Code -->
    </head>
    <body>
        <header>
            <div class="logo-area">
                <div class="logo-icon">C</div>
                <div class="brand-title">
                    <h1>Converis CRM</h1>
                    <p>Powered by <strong>Martik</strong></p>
                </div>
            </div>
        </header>
        <div class="container">
            <h2>Painel Principal do CRM</h2>
            <p>O seu sistema CRM completo está configurado, otimizado e pronto para gerir os seus clientes com o selo de qualidade <strong>Martik</strong>.</p>
            <div class="card">
                <h3>Módulos Ativos</h3>
                <p>✅ Gestão de Leads, Funil de Vendas e Pixel do Meta a monitorizar o tráfego.</p>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run()
