from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

clientes_data = []

@app.route('/api/clientes', methods=['POST'])
def recibir_clientes():
    global clientes_data
    if request.headers.get("X-Cliente-ID") != "1":
        return jsonify({"error": "Cliente no autorizado"}), 403
    clientes_data = request.get_json()
    return jsonify({"status": "ok", "recibidos": len(clientes_data)})

@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    if request.headers.get("X-Cliente-ID") != "1":
        return jsonify({"error": "Cliente no autorizado"}), 403
    return jsonify(clientes_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)