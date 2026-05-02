import os
from dotenv import load_dotenv

load_dotenv()

from flask import Blueprint, jsonify, request
from app.BD.BDapi import BaseDeDatos

# Creamos el blueprint
registrar_bp = Blueprint("registrar", __name__)
historial_bp = Blueprint("historial", __name__)
registradora_bp = Blueprint("registradora", __name__)
resumen_bp = Blueprint("resumen", __name__)
transacciones_bp = Blueprint("transacciones", __name__)
empleados_bp = Blueprint("empleados", __name__)
cambios_bp = Blueprint("cambios", __name__)

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
        valor_formateado = formatear_numero(valor)
        return jsonify({
        "success": True,
        "titulo_mensaje": f"REGISTRADO EN {nombre_tabla}",
        "cuerpo_mensaje": f"* DESCRIPCION: {descripcion}\n\n* VALOR: {valor_formateado}"
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

    if datos is None:
        return jsonify({
            "success": False,
            "data": []
        }), 500
    
    return jsonify({
        "success": True,
        "data": datos
    }), 200


@historial_bp.route("/opciones", methods=["GET"])
def consultar_opciones():
    autorizado = verificar(request.headers.get("Authorization"))
    if not autorizado:
        return jsonify({
            "success": False,
            "data": []
        }), 401

    opciones = bd.consultar_opciones(request.args.get("nombre_tabla"))

    if opciones is None:
        return jsonify({
            "success": False,
            "data": []
        }), 500
    
    return jsonify({
        "success": True,
        "data": opciones
    }), 200

@resumen_bp.route("/", methods=["GET"])
def obtener_resumen_general():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "data": []
        }), 401

    result_resumen = bd.obtener_resumen_general(request.args.get("fecha_inicio"), request.args.get("fecha_final"), request.args.get("nombre_tabla"))
    #print(f"resumen en el endpoint {result_resumen}\n")
    if result_resumen is None:
        return jsonify({
            "success": False,
            "data": []
        }), 500

    return jsonify({
        "success": True,
        "data": result_resumen
    }), 200

@resumen_bp.route("/totales", methods=["GET"])
def obtener_totales_por_fecha():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "data": 0
        }), 401

    result_total = bd.obtener_totales_por_fecha(request.args.get("fecha_inicio"), request.args.get("fecha_final"), request.args.get("nombre_tabla"))
    if result_total is None:
        return jsonify({
            "success": False,
            "data": 0
        }), 500

    return jsonify({
        "success": True,
        "data": result_total
    }), 200

@resumen_bp.route("/acumulado", methods=["GET"])
def obtener_acumulado():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "data": 0
        }), 401
    
    fecha_final_rec = request.args.get("fecha_final")
    num_quincena = request.args.get("num_quincena")
    if num_quincena is None:
        fecha_inicio_formateada = fecha_final_rec[:7] + "-01"
        fecha_final_formateada = fecha_final_rec[:7] + "-32"
    else:
        if num_quincena == "1°":
            fecha_inicio_formateada = fecha_final_rec[:7] + "-01"
            fecha_final_formateada = fecha_final_rec[:7] + "-16"
        else:
            fecha_inicio_formateada = fecha_final_rec[:7] + "-16"
            fecha_final_formateada = fecha_final_rec[:7] + "-32"
    
    result_acumulado = bd.obtener_acumulado(fecha_inicio_formateada, fecha_final_formateada, request.args.get("nombre_tabla"))

    if result_acumulado is None:
        return jsonify({
            "success": False,
            "data": 0
        }), 500

    return jsonify({
        "success": True,
        "data": result_acumulado
    }), 200

@resumen_bp.route("/totales/ventas", methods=["GET"])
def obtener_total_ventas():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "data": 0
        }), 401

    result_total_ventas = bd.obtener_total_ventas(request.args.get("fecha_inicio"), request.args.get("fecha_final"))

    if result_total_ventas is None:
        return jsonify({
            "success": False,
            "data": 0
        }), 500

    return jsonify({
        "success": True,
        "data": result_total_ventas
    }), 200

@resumen_bp.route("/acumulado/ventas", methods=["GET"])
def obtener_acumulado_ventas():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "data": 0
        }), 401

    fecha_final_rec = request.args.get("fecha_final")
    fecha_inicio_formateada = fecha_final_rec[:7] + "-01"
    fecha_final_formateada = fecha_final_rec[:7] + "-32"

    result_acumulado_ventas = bd.obtener_acumulado_ventas(fecha_inicio_formateada, fecha_final_formateada)

    if result_acumulado_ventas is None:
        return jsonify({
            "success": False,
            "data": 0
        }), 500

    return jsonify({
        "success": True,
        "data": result_acumulado_ventas
    }), 200

@resumen_bp.route("/totales/gastado", methods=["GET"])
def obtener_total_gastado():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "data": 0
        }), 401

    result_total_gastado = bd.obtener_total_gastado(request.args.get("fecha_inicio"), request.args.get("fecha_final"))

    if result_total_gastado is None:
        return jsonify({
            "success": False,
            "data": 0
        }), 500

    return jsonify({
        "success": True,
        "data": result_total_gastado
    }), 200

@resumen_bp.route("/acumulado/gastado", methods=["GET"])
def obtener_acumulado_total_gastado():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "data": 0
        }), 401

    fecha_final_rec = request.args.get("fecha_final")
    fecha_inicio_formateada = fecha_final_rec[:7] + "-01"
    fecha_final_formateada = fecha_final_rec[:7] + "-32"

    result_acumulado_total_gastado = bd.obtener_acumulado_total_gastado(fecha_inicio_formateada, fecha_final_formateada)

    if result_acumulado_total_gastado is None:
        return jsonify({
            "success": False,
            "data": 0
        }), 500

    return jsonify({
        "success": True,
        "data": result_acumulado_total_gastado
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
    

@transacciones_bp.route("/", methods=["POST"])
def recibir_transaccion():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "titulo_mensaje": "No autorizado",
            "cuerpo_mensaje": "Token de autorización inválido"
        }), 401

    body = request.get_json()
    if not body:
        return jsonify({"success": False, "titulo_mensaje": "No data received", "cuerpo_mensaje": "No se enviaron datos para guardar la transaccion"}), 400

    descripcion = body.get("descripcion")
    valor = body.get("valor")
    tipo = body.get("tipo")
    result_recibir_transaccion = bd.recibir_transaccion(descripcion, valor, tipo)
    
    tipoRegistro = "INGRESO" if valor > 0 else "EGRESO"
    monto_formateado = formatear_numero(valor)
    if result_recibir_transaccion:
        return jsonify({
        "success": True,
        "titulo_mensaje": f"{tipoRegistro} GUARDADO CON ÉXITO",
        "cuerpo_mensaje": f"Se guardó '{descripcion}' de ${monto_formateado} proveniente de {tipo} en la BD"
    }), 201
    else:
        return jsonify({
            "success": False,
            "titulo_mensaje": f"ERROR AL GUARDAR EL {tipoRegistro}",
            "cuerpo_mensaje": f"NO SE PUDO guardar '{descripcion}' de ${monto_formateado} proveniente de {tipo} en la BD"
        }), 500


@empleados_bp.route("/prestamos", methods=["POST"])
def registrar_prestamo_emp():
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return jsonify({
            "success": False,
            "titulo_mensaje": "No autorizado",
            "cuerpo_mensaje": "Token de autorización inválido"
        }), 401

    body = request.get_json()
    if not body:
        return jsonify({"success": False, "titulo_mensaje": "No data received", "cuerpo_mensaje": "No se enviaron datos para guardar el prestamo"}), 400

    descripcion = body.get("descripcion")
    valor = body.get("valor")
    empleado = body.get("empleado")
    result_registrar_prestamo_emp = bd.registrar_prestamo_emp(descripcion, valor, empleado)
    
    valor_formateado = formatear_numero(valor)
    if result_registrar_prestamo_emp:
        return jsonify({
        "success": True,
        "titulo_mensaje": f"PRÉSTAMO A {empleado} GUARDADO",
        "cuerpo_mensaje": f"* DESCRIPCION: {descripcion}\n\n* VALOR: ${valor_formateado}"
    }), 201
    else:
        return jsonify({
            "success": False,
            "titulo_mensaje": f"ERROR AL GUARDAR EL PRESTAMO EN LA BD",
            "cuerpo_mensaje": f"NO SE PUDO guardar el prestamo de {empleado} por ${valor_formateado}, inténtalo más tarde"
        }), 500


@empleados_bp.route("/historialDiario", methods=["GET"])
def obtener_historial_diario_emp():
    autorizado = verificar(request.headers.get("Authorization"))
    if not autorizado:
        return jsonify({
            "success": False,
            "data": []
        }), 401

    datos = bd.obtener_historial_diario_emp(request.args.get("dia_a_consultar"))

    if datos is None:
        return jsonify({
            "success": False,
            "data": []
        }), 500
    
    return jsonify({
        "success": True,
        "data": datos
    }), 200


@cambios_bp.route("/delete/<int:id>/<string:tipo>", methods=["DELETE"])
def eliminar_cambio(id, tipo):
    token = request.headers.get("Authorization")
    autorizado = verificar(token)
    if not autorizado:
        return '', 401

    result_eliminar = bd.eliminar_registro(id, tipo)

    if result_eliminar:
        return '', 204
    else:
        return '', 500


# =================Función para verificar el token de autorización =============================
def verificar(token):
    if token != f"Bearer {os.getenv('TOKEN_API')}":
        return False
    return True

def formatear_numero(valor):
    if isinstance(valor, int):
        return f"{valor:,}".replace(",", ".")
    else:
        return valor