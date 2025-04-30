from flask import Flask, request, jsonify, abort,render_template
import threading
from rs232 import rs232Comunication
from MecanismLogic import Manager
from database.SqliteManager import SqliteManager
from dotenv import load_dotenv
import os

load_dotenv()
mode = os.getenv("MODE","COLISEO")
#version 4.0
app = Flask(__name__)
stop_event = threading.Event()


@app.route('/')
def home():
    return "API V1.1"

from flask import Flask, request, jsonify

@app.route('/api/mecanism', methods=['GET', 'POST'])
def mecanism_api():
    if request.method == 'GET':
        return jsonify({"message": "Método GET no implementado"}), 200

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No se recibió un JSON válido"}), 400

    operation = json_data.get('operation')
    if not operation:
        return jsonify({"error": "El campo 'operation' es obligatorio"}), 400

    operations_map = {
        'read_sensor': (manager.read_sensor, "Sensor leído"),
        'generate_right_pass': (manager.generate_right_pass, "Pase derecho generado"),
        'generate_left_pass': (manager.generate_left_pass, "Pase izquierdo generado"),
        'test_all_locks': (manager.test_all_locks, "Cerradura testeada"),
        'test_arrow_indicators': (manager.test_arrow_indicators, "Luz LED testeada"),
        'generate_special_pass': (manager.generate_special_pass, "Pase especial generado"),
        'open_special_door': (manager.open_special_door, "Puerta especial abriéndose"),
        'close_special_door': (manager.close_special_door, "Puerta especial cerrándose"),
    }
    action = operations_map.get(operation)
    if not action:
        return jsonify({"error": f"Operación '{operation}' no válida"}), 404

    try:
        result = action[0]()  # Ejecutar función
        msg = action[1]
        return jsonify({
            "result": result,
            "status": 200,
            "message": msg
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Ocurrió un error al ejecutar la operación",
            "details": str(e)
        }), 500

    
@app.route('/api/database', methods=['GET', 'POST'])
def db_Api():
    if request.method == 'GET':
        operation = request.args.get('operation')
        if operation == "transactions":
            return  database.get_transactions()
        elif operation == "last_transactions":
            result = database.get_last_transactions()
            print(result)
            return  jsonify({'result':result})
        elif operation['operation'] == "parameters":
            return database.get_parameters()
        else:
            return 'bad request!', 400
    elif request.method == 'POST':
        params = request.get_json()
        if not params:
            return jsonify({"error": "No se recibió JSON"}), 400
        try:
            _data = (params['place'],params['created_at'],params['bus_station_id'],params['lat'],params['lon'])
            database.uuid = params['uuid']
            database.place = params['place']
            database.lat = params['lat']
            database.lon = params['lon']
            database.insert_parameter(_data)
        except:
            return jsonify({"message": "No se recibió JSON Adecuadamente"}), 400
        
        return jsonify({"message": "Datos recibidos"}), 200
    




@app.route("/datos")
def datos():
    return rs232.getData()

if __name__ == "__main__":
    rs232 = rs232Comunication( stop_event=stop_event)
    manager = Manager(stop_event=stop_event,rs232=rs232,mode=mode)

    database = SqliteManager(stop_event=stop_event,rs232=rs232) 
    init_params = database.currentParameters()
    if init_params != None:
        database.uuid = init_params[9]
        database.place = init_params[1]
        database.lat = init_params[10]
        database.lon = init_params[11]
    rs232.start()
    manager.start()
    database.start()
    try:
        app.run(host='0.0.0.0', port=5000,use_reloader=False)
    finally:
        stop_event.set()
        rs232.join()
        manager.join()
        database.join()
        print("programa terminado!")
