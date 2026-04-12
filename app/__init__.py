from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Permite peticiones desde Android

    # Registrar los "blueprints" (grupos de rutas)
    from app.routes.usuarios import usuarios_bp
    app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")

    return app