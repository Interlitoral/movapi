from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import pyodbc
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas y orígenes

# CONFIGURÁ ESTOS DATOS SEGÚN TU ENTORNO
#server = 'localhost\\SQLEXPRESS'  # o simplemente 'localhost' si no tenés instancia nombrada
server = 'INTERLITORAL'
database = 'Movint'
username = 'Axoft'
password = 'Axoft'

connection_string = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={server};
    DATABASE={database};
    UID={username};
    PWD={password};
"""

# Configuración de logs
log_file = 'movapi.log'
log_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[log_handler]
)

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
    
@app.route('/ping')
def ping():
    return jsonify({"mensaje": "API activa"})

@app.route('/vendedores')
def vendedores():
    sql = "SELECT COD_VENDED, NOMBRE_VEN FROM GVA23"  # ejemplo
    return jsonify(ejecutar_consulta(sql))

@app.route('/clientes')
def clientes():
    sql = "SELECT COD_CLIENT, RAZON_SOCI FROM GVA14"  # ejemplo
    return jsonify(ejecutar_consulta(sql))

@app.route('/articulos')
def articulos():
    sql = "SELECT COD_ARTICU, DESCRIPCIO FROM STA11"  # ejemplo
    return jsonify(ejecutar_consulta(sql))

@app.route('/precios')
def precios():
    sql = "SELECT COD_ARTICU, COD_LISTA, PRECIO FROM GVA17"  # ejemplo
    return jsonify(ejecutar_consulta(sql))


@app.route('/pedidos', methods=['POST'])
def insertar_pedido_completo():
    datos = request.get_json()
    encabezado = datos.get('encabezado')
    renglones = datos.get('renglones')

    if not encabezado or not renglones:
        logging.warning("Faltan datos de encabezado o renglones")
        return jsonify({'error': 'Faltan datos de encabezado o renglones'}), 400        
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        logging.info(f"Insertando pedido ID_TRANSACCION: {encabezado['id_transaccion']}")
        
        fecha_ped = parse_fecha(encabezado.get('fecha_ped'))

        # Insertar encabezado SIN fechas
        cursor.execute("""
            INSERT INTO A1_PEDIDOS_ENCABEZADO (
                ID_TRANSACCION, ID_DISPOSITIVO, FECHA_PED, COD_CLIENTE, NRO_LISTA,
                COND_VTA, COD_VENDEDOR, ESTADO, HABITUAL,
                NRO_PEDIDO_DISPOSITIVO, PORC_DESC, TOTAL_PEDI, LEYENDA_1
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            encabezado['id_transaccion'],
            encabezado.get('id_dispositivo'),
            fecha_ped,
            encabezado.get('cod_cliente'),
            encabezado.get('nro_lista'),
            encabezado.get('cond_vta'),
            encabezado.get('cod_vendedor'),
            encabezado.get('estado'),
            encabezado.get('habitual'),
            encabezado.get('nro_pedido_dispositivo'),
            encabezado.get('porc_desc'),
            encabezado.get('total_pedi'),
            encabezado.get('leyenda_1'),
        ))

        # Insertar renglones SIN fecha_entrega
        for renglon in renglones:
            cursor.execute("""
                INSERT INTO A1_PEDIDOS_RENGLONES (
                    ID_TRANSACCION, ID_DISPOSITIVO, COD_ARTICU,
                    CANTIDAD, N_RENGLON, ESTADO, NRO_PEDIDO_DISPOSITIVO,
                    PORC_DESC, PRECIO, DESC_ADIC
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                renglon['id_transaccion'],
                renglon.get('id_dispositivo'),
                renglon.get('cod_articu'),
                renglon.get('cantidad'),
                renglon.get('n_renglon'),
                renglon.get('estado'),
                renglon.get('nro_pedido_dispositivo'),
                renglon.get('porc_desc'),
                renglon.get('precio'),
                renglon.get('desc_adic'),
            ))

        conn.commit()        
        conn.close()
        
        logging.info(f"✅ Pedido {encabezado['id_transaccion']} insertado correctamente")
        return jsonify({'mensaje': 'Pedido registrado correctamente!!'}), 201

    except Exception as e:
        print("❌ Error:", str(e))
        logging.error(f"❌ Error al insertar pedido: {str(e)}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return jsonify({'error': str(e)}), 500

@app.route('/procesar_pedido', methods=['POST'])
def procesar_pedido():
    datos = request.get_json()
    id_transaccion = datos.get('id_transaccion')

    if not id_transaccion:
        return jsonify({'error': 'Falta el parámetro id_transaccion'}), 400

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Ejecutar SP
        cursor.execute("EXEC A3_PROCESAR_PEDIDO ?", (id_transaccion,))
        conn.commit()
        conn.close()

        logging.info(f"✅ SP A3_PROCESAR_PEDIDO ejecutado correctamente para ID_TRANSACCION={id_transaccion}")
        return jsonify({'mensaje': 'Procedimiento ejecutado correctamente'}), 200

    except Exception as e:
        logging.error(f"❌ Error al ejecutar SP A3_PROCESAR_PEDIDO con ID_TRANSACCION={id_transaccion}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# @app.route('/test_insert')
# def test_insert():
    # try:
        # conn = pyodbc.connect(connection_string)
        # cursor = conn.cursor()
        # cursor.execute("""
            # INSERT INTO A1_PEDIDOS_ENCABEZADO (
                # ID_TRANSACCION, ID_DISPOSITIVO, COD_CLIENTE, NRO_LISTA,
                # COND_VTA, COD_VENDEDOR, ESTADO, HABITUAL, FECHA_ING,
                # FECHA_PED, NRO_PEDIDO_DISPOSITIVO, PORC_DESC, TOTAL_PEDI,
                # LEYENDA_1
            # )
            # VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            # 'TEST123', 'TEST123', '0001', '01',
            # '01', '01', 'P', 0, '2025-05-29',
            # '2025-05-29', '00001', 0, 123.45,
            # '🧪 Test desde API'
        # )
        # conn.commit()
        # conn.close()
        # return jsonify({'resultado': 'Insert test exitoso'})
    # except Exception as e:
        # return jsonify({'error': str(e)})
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
            