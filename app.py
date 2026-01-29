from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_bcv_price():
    try:
        # Usamos la API de el_it_venezolano que es muy estable para Render
        url = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv"
        response = requests.get(url, timeout=10)
        data = response.json()
        # Accedemos directamente al valor del precio
        return data['monedas']['bcv']['price']
    except Exception as e:
        print(f"Error BCV: {e}")
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
            "transAmount": "500" # Filtramos por un monto mínimo para evitar órdenes 'basura'
        }
        headers = { "User-Agent": "Mozilla/5.0" }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        if data['success'] and data['data']:
            # Solo promediamos si el precio es razonable (evitamos errores de API)
            precios = [float(adv['adv']['price']) for adv in data['data']]
            promedio = sum(precios) / len(precios)
            return round(promedio, 2)
        return "N/A"
    except:
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
