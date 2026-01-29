from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

def get_bcv_price():
    # Intentamos con 3 fuentes distintas para asegurar que el BCV siempre cargue
    urls = [
        "https://ve.dolarapi.com/v1/dolares/oficial",
        "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv",
        "https://api.exchangerate-api.com/v4/latest/USD"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, timeout=7)
            if res.status_code == 200:
                data = res.json()
                # Opción 1: DolarApi
                if 'promedio' in data: 
                    return f"{data['promedio']:.2f}"
                # Opción 2: PyDolar
                if 'monedas' in data: 
                    return f"{data['monedas']['bcv']['price']:.2f}"
                # Opción 3: Backup internacional (USD a VES)
                if 'rates' in data: 
                    return f"{data['rates'].get('VES', 'N/A'):.2f}"
        except:
            continue
    return "N/A"

def get_binance_p2p():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": False,
            "page": 1,
            "rows": 10,
            "publisherType": None,
            "tradeType": "BUY",
            "transAmount": "500" # Filtro para precios reales de mercado
        }
        headers = { "User-Agent": "Mozilla/5.0" }
        
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        data = res.json()
        
        if data.get('success') and data.get('data'):
            precios = [float(adv['adv']['price']) for adv in data['data']]
            promedio = sum(precios) / len(precios)
            return f"{promedio:.2f}"
    except Exception as e:
        print(f"Error Binance: {e}")
    return "Error"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/precios')
def api_precios():
    return jsonify({
        'binance': get_binance_p2p(),
        'bcv': get_bcv_price()
    })

if __name__ == '__main__':
    # Configuración vital para Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
