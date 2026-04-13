from flask import Flask
from flask_cors import CORS
from app.BD.BDapi import BaseDeDatos

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Android
db = BaseDeDatos()

# Registrar los "blueprints" (grupos de rutas)
from app.routes.usuarios import usuarios_bp
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")

if __name__ == "__main__":
    app.run()