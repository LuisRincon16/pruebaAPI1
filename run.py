from flask import Flask
from flask_cors import CORS
from app.BD.BDapi import BaseDeDatos

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Android
db = BaseDeDatos()

# Registrar los "blueprints" (grupos de rutas)
from app.routes.endpoints import registrar_bp
from app.routes.endpoints import historial_bp
from app.routes.endpoints import registradora_bp
app.register_blueprint(registrar_bp, url_prefix="/api/registrar")
app.register_blueprint(historial_bp, url_prefix="/api/historial")
app.register_blueprint(registradora_bp, url_prefix="/api/registradora")

if __name__ == "__main__":
    app.run()