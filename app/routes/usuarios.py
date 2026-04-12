from flask import Blueprint, jsonify, request

# Creamos el blueprint
usuarios_bp = Blueprint("usuarios", __name__)

# Base de datos simulada (en producción usarías PostgreSQL, MySQL, etc.)
USUARIOS = [
    {"id": 1, "nombre": "Ana García",   "email": "ana@email.com",   "edad": 28},
    {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com", "edad": 34},
    {"id": 3, "nombre": "María Ruiz",   "email": "maria@email.com",  "edad": 22},
]


# GET /api/usuarios/
@usuarios_bp.route("/", methods=["GET"])
def obtener_todos():
    """Devuelve la lista completa de usuarios"""
    return jsonify({
        "success": True,
        "data": USUARIOS,
        "total": len(USUARIOS)
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


# POST /api/usuarios/
@usuarios_bp.route("/", methods=["POST"])
def crear_usuario():
    """Recibe datos JSON y crea un nuevo usuario"""
    body = request.get_json()

    if not body:
        return jsonify({"success": False, "mensaje": "No se enviaron datos"}), 400

    nuevo = {
        "id": len(USUARIOS) + 1,
        "nombre": body.get("nombre"),
        "email": body.get("email"),
        "edad": body.get("edad")
    }
    USUARIOS.append(nuevo)

    return jsonify({
        "success": True,
        "mensaje": "Usuario creado",
        "data": nuevo
    }), 201