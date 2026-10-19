from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converis CRM - Martik</title>
    <style>
        * { box-sizing: border-box; font-family: sans-serif; }
        body { background-color: #f4f7f6; margin: 0; padding: 0; }
        header { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; }
        .logo-box { background: #ff6b6b; color: white; font-weight: bold; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .container { max-width: 1100px; margin: 20px auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 25px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card h3 { margin: 0 0 10px 0; color: #555; font-size: 14px; }
        .card .number { font-size: 24px; font-weight: bold; color: #1e3c72; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
        th { background-color: #f8f9fa; color: #333; }
        .status { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; background: #e3f2fd; color: #1976d2; }
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
</head>
<body>
    <header>
        <div style="display:flex; align-items:center; gap:12px;">
            <div class="logo-box">C</div>
            <div>
                <h2 style="margin:0; font-size:18px;">Converis CRM</h2>
                <span style="font-size:11px; opacity:0.8;">Powered by <strong>Martik</strong></span>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="grid">
            <div class="card">
                <h3>TOTAL DE LEADS</h3>
                <div class="number">2</div>
            </div>
            <div class="card">
                <h3>OPORTUNIDADES</h3>
                <div class="number">R$ 4.700</div>
            </div>
            <div class="card">
                <h3>PIXEL DO META</h3>
                <div class="number" style="color:#2e7d32; font-size:16px;">🟢 Ativo</div>
            </div>
        </div>

        <h3>Gestão de Leads & Oportunidades</h3>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>E-mail</th>
                    <th>Status</th>
                    <th>Valor Estimado</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>#1</td>
                    <td><strong>João Silva</strong></td>
                    <td>joao@email.com</td>
                    <td><span class="status">Novo Lead</span></td>
                    <td>R$ 1.500</td>
                </tr>
                <tr>
                    <td>#2</td>
                    <td><strong>Maria Santos</strong></td>
                    <td>maria@email.com</td>
                    <td><span class="status">Em Negociação</span></td>
                    <td>R$ 3.200</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>'''

if __name__ == '__main__':
    app.run()
