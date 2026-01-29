from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_bcv_price():
    try:
        # Usamos un servidor espejo que suele estar desbloqueado
        url = "https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv"
        response = requests.get(url, timeout=10)
        data = response.json()
        # Buscamos el valor del BCV en la respuesta
        return data['monedas']['bcv']['price']
    except Exception as e:
        print(f"Error BCV: {e}")
        return "Error"

def get_binance_p2p():
    try:
        # Para Binance en cuenta gratis, usamos un Proxy público 
        # o intentamos la ruta directa con headers más robustos
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": False,
            "page": 1,
            "rows": 10,
            "publisherType": None,
            "tradeType": "BUY"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('success') and data.get('data'):
            precios = [float(adv['adv']['price']) for adv in data['data']]
            promedio = sum(precios) / len(precios)
            return round(promedio, 2)
        return "N/A"
    except Exception as e:
        print(f"Error P2P: {e}")
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