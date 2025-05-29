from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import pyodbc
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas y orígenes

def conectar_db(cliente_id):
    cfg = CONEXIONES.get(cliente_id)
    if not cfg:
        raise Exception("Cliente no configurado")
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={cfg['server']};"
        f"DATABASE={cfg['database']};"
        f"UID={cfg['username']};"
        f"PWD={cfg['password']}"
    )
    return pyodbc.connect(conn_str)
    
# Función genérica para hacer consultas
def ejecutar_consulta(sql):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(sql)
        columnas = [col[0] for col in cursor.description]
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        conn.close()
        return resultados
    except Exception as e:
        return {"error": str(e)}

def parse_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y")
    except:
        return None
    
@app.route('/api/clientes')
def clientes():
    cliente_id = request.headers.get('X-Cliente-ID')
    if not cliente_id:
        return jsonify({"error": "Falta X-Cliente-ID"}), 400
    try:
        conn = conectar_db(cliente_id)
        cursor = conn.cursor()
        cursor.execute("SELECT COD_CLIENT, RAZON_SOCI FROM GVA14")
        cols = [col[0] for col in cursor.description]
        rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
            