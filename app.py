from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_bcv_price():
    try:
        # Usamos la API más estable para el dólar oficial en Render
        response = requests.get("https://ve.dolarapi.com/v1/dolares/oficial", timeout=10)
        if response.status_code == 200:
            return response.json().get('promedio', 'Error')
        return "Error API"
    except Exception as e:
        return "Error Conexión"

def get_binance_p2p_avg():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        # Payload específico para USDT en Bolívares
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": False,
            "page": 1,
            "rows": 10,
            "publisherType": None,
            "tradeType": "BUY"
        }
        # Headers para que Binance no nos bloquee
        headers = { "User-Agent": "Mozilla/5.0" }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('success') and data.get('data'):
            # Sacamos el promedio de los primeros 10
            prices = [float(adv['adv']['price']) for adv in data['data']]
            avg = sum(prices) / len(prices)
            return round(avg, 2)
        return "N/A"
    except:
        return "Error P2P"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/precios')
def api_precios():
    return jsonify({
        'binance': get_binance_p2p_avg(),
        'bcv': get_bcv_price()
    })

if __name__ == '__main__':
    app.run()
