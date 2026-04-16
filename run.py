from flask import Flask
from flask_cors import CORS
from app.BD.BDapi import BaseDeDatos

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Android
db = BaseDeDatos()

# Registrar los "blueprints" (grupos de rutas)
from app.routes.usuarios import usuarios_bp
from app.routes.usuarios import historial_bp
from app.routes.usuarios import registradora_bp
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(historial_bp, url_prefix="/api/historial")
app.register_blueprint(registradora_bp, url_prefix="/api/registradora")

if __name__ == "__main__":
    app.run()