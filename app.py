from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# Función BCV mejorada con manejo de errores silencioso
def get_bcv_price():
    url = "https://ve.dolarapi.com/v1/dolares/oficial"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return f"{res.json().get('promedio', 'N/A')}"
    except:
        pass
    return "N/A"

# Función Binance enfocada en velocidad
def get_binance_p2p():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT", "fiat": "VES", "merchantCheck": False,
        "page": 1, "rows": 10, "publisherType": None,
        "tradeType": "BUY", "transAmount": "500"
    }
    try:
        res = requests.post(url, json=payload, timeout=5)
        data = res.json()
        if data.get('data'):
            prices = [float(adv['adv']['price']) for adv in data['data']]
            return f"{sum(prices) / len(prices):.2f}"
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
    # Render necesita que el host sea 0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
