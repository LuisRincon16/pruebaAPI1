import os
from dotenv import load_dotenv

load_dotenv()

from flask import Blueprint, jsonify, request
from app.BD.BDapi import BaseDeDatos

# Creamos el blueprint
registrar_bp = Blueprint("registrar", __name__)
historial_bp = Blueprint("historial", __name__)
registradora_bp = Blueprint("registradora", __name__)

# Instanciamos la base de datos
bd = BaseDeDatos()

# POST /api/registrar/
@registrar_bp.route("/", methods=["POST"])
def agregar_dato():
    autorizado = verificar(request.headers.get("Authorization"))
    if not autorizado:
        return jsonify({
            "success": False,
            "titulo_mensaje": "Token de autorización inválido",
            "cuerpo_mensaje": "SUERTE .!."
        }), 401
    
    #si está autorizado, recibe el JSON con los datos para agregar
    body = request.get_json()
    if not body:
        return jsonify({"success": False,
                        "titulo_mensaje": "No se enviaron datos",
                        "cuerpo_mensaje": "Enviar datos por favor"
                        }), 400
    
    nombre_tabla = body.get("nombre_tabla")
    descripcion = body.get("descripcion")
    valor = body.get("valor")
    result_agregar_dato = bd.agregar_dato(nombre_tabla, descripcion, valor)

    if result_agregar_dato:
        return jsonify({
        "success": True,
        "titulo_mensaje": f"REGISTRADO EN {nombre_tabla}",
        "cuerpo_mensaje": f"* DESCRIPCION: {descripcion}\n* VALOR: {valor}"
    }), 201
    else:
        return jsonify({
            "success": False,
            "titulo_mensaje": "ERROR DE CONEXIÓN :(",
            "cuerpo_mensaje": "No se pudo agregar el registro a la BD por algun fallo de conexion."
        }), 500


#recibir historial de datos de las tres tablas
@historial_bp.route("/", methods=["GET"])
def obtener_historial():
    autorizado = verificar(request.headers.get("Authorization"))
    if not autorizado:
        return jsonify({
            "success": False,
            "data": []
        }), 401

    datos = bd.obtener_historial(request.args.get("fecha_inicio"),
                                 request.args.get("fecha_final"),
                                 request.args.get("descripcion"))
    #print(datos)

    if datos is None:
        return jsonify({
            "success": False,
            "data": []
        }), 500
    
    return jsonify({
        "success": True,
        "data": datos
    }), 200



#----------------- ENDPOINTS PARA LAS VENTAS ----------------------

@registradora_bp.route("/ventas", methods=["POST"])
def agregar_venta():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": "Token de autorización inválido"
        }), 401

    body = request.get_json()
    if not body:
        return jsonify({"success": False, "mensaje": "No se enviaron datos"}), 400

    result_agregar_venta = bd.agregar_venta(body.get("fecha"), body.get("hora"), body.get("monto"), body.get("estado"))

    if result_agregar_venta:
        return jsonify({
        "success": True,
        "mensaje": f"Venta agregada con éxito."
    }), 201
    else:
        return jsonify({
            "success": False,
            "mensaje": "No se pudo agregar la venta a la base de datos por algun fallo de conexion."
        }), 500
    

@registradora_bp.route("/consultas", methods=["GET"])
def consultar_ventas():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": "Token de autorización inválido"
        }), 401

    datos = bd.consultar_ventas(request.args.get("fecha_inicio"), request.args.get("fecha_final"))

    if datos is None:
        return jsonify({
            "success": False,
            "data": []
        }), 500
    
    return jsonify({
        "success": True,
        "data": datos
    }), 200

@registradora_bp.route("/ventas/<int:id_venta>", methods=["GET"])
def consultar_venta_por_id(id_venta):
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": "Token de autorización inválido"
        }), 401

    dato = bd.consultar_venta_por_id(id_venta)

    if dato is None:
        return jsonify({
            "success": False,
            "data": None
        }), 500
    
    return jsonify({
        "success": True,
        "data": dato      #puede ser un DATO si encuentra la venta o FALSE si no hay ventas por ese ID
    }), 200

@registradora_bp.route("/venta_total", methods=["GET"])
def total_ventas():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": "Token de autorización inválido"
        }), 401

    total = bd.total_vendido(request.args.get("fecha_inicio"), request.args.get("fecha_final"))

    if total is None:
        return jsonify({
            "success": False,
            "data": None
        }), 500
    
    return jsonify({
        "success": True,
        "data": total        #puede ser un DATO si encuentra un TOTAL o FALSE si no hay ningun TOTAL para ese rango de fechas
    }), 200

@registradora_bp.route("/ventas/<int:id_venta>", methods=["DELETE"])
def eliminar_venta_por_id(id_venta):
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": "Token de autorización inválido"
        }), 401

    result_eliminar = bd.eliminar_venta_por_id(id_venta)

    if result_eliminar:
        return jsonify({
            "success": True,
            "mensaje": f"Venta con ID {id_venta} eliminada con éxito."
        }), 200
    else:
        return jsonify({
            "success": False,
            "mensaje": f"No se pudo eliminar la venta con ID {id_venta} por algun fallo de conexion."
        }), 500
    
@registradora_bp.route("/ventas_pendientes", methods=["POST"])
def agregar_ventas_pendientes():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": "Token de autorización inválido"
        }), 401
    
    body = request.get_json()
    if not body:
        return jsonify({"success": False, "mensaje": "No se enviaron datos"}), 400

    result_agregar_pendientes = bd.agregar_ventas_pendientes(body)

    if result_agregar_pendientes:
        return jsonify({
        "success": True,
        "mensaje": f"Ventas pendientes agregadas con éxito."
    }), 201
    else:
        return jsonify({
            "success": False,
            "mensaje": f"No se pudieron agregar las ventas pendientes a la base de datos por algun fallo de conexion. Error: {result_agregar_pendientes}"
        }), 500

# =================Función para verificar el token de autorización =============================
def verificar(token):
    if token != f"Bearer {os.getenv('TOKEN_API')}":
        return False
    return True