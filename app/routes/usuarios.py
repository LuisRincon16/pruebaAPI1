from flask import Blueprint, jsonify, request
from app.BD.BDapi import BaseDeDatos

# Creamos el blueprint
usuarios_bp = Blueprint("usuarios", __name__)

# Instanciamos la base de datos
bd = BaseDeDatos()

# POST /api/usuarios/
@usuarios_bp.route("/", methods=["POST"])
def agregar_dato():
    """Recibe datos JSON y crea un registro"""
    body = request.get_json()

    if not body:
        return jsonify({"success": False, "mensaje": "No se enviaron datos"}), 400

    bd.agregar_dato(body.get("nombre_tabla"), body.get("descripcion"), body.get("valor"))

    return jsonify({
        "success": True,
        "mensaje": f"Registro de {body.get('nombre_tabla')} creado"
    }), 201


# GET /api/usuarios/
@usuarios_bp.route("/", methods=["GET"])
def obtener_todos():
    """Devuelve la lista completa de usuarios"""
    return jsonify({
        "success": True,
        "data": "TODO BIEN"
    }), 200


# GET /api/usuarios/<id>
@usuarios_bp.route("/<int:usuario_id>", methods=["GET"])
def obtener_uno(usuario_id):
    """Devuelve un usuario por su ID"""
    usuario = next((u for u in USUARIOS if u["id"] == usuario_id), None)

    if usuario is None:
        return jsonify({
            "success": False,
            "mensaje": f"Usuario con id {usuario_id} no encontrado"
        }), 404

    return jsonify({
        "success": True,
        "data": usuario
    }), 200
