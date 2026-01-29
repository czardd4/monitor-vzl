from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_bcv_price():
    # Intentamos con la API más estable para servidores internacionales
    urls = [
        "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv",
        "https://ve.dolarapi.com/v1/dolares/oficial"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Dependiendo de qué API responda, extraemos el dato
                if 'monedas' in data:
                    return data['monedas']['bcv']['price']
                return data.get('promedio', 'N/A')
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
            "transAmount": "500" # FILTRO CLAVE: Montos reales de mercado
        }
        headers = { "User-Agent": "Mozilla/5.0" }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('success') and data.get('data'):
            # Extraemos precios de órdenes reales (no anuncios basura)
            precios = [float(adv['adv']['price']) for adv in data['data']]
            promedio = sum(precios) / len(precios)
            return round(promedio, 2)
    except:
        pass
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
    app.run()
