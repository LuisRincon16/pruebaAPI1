from flask import Flask
from flask_cors import CORS
from app.BD.BDapi import BaseDeDatos
import os

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Android
db = BaseDeDatos()

# Registrar los "blueprints" (grupos de rutas)
from app.routes.endpoints import registrar_bp
from app.routes.endpoints import historial_bp
from app.routes.endpoints import registradora_bp
from app.routes.endpoints import resumen_bp
from app.routes.endpoints import transacciones_bp
from app.routes.endpoints import empleados_bp
from app.routes.endpoints import cambios_bp
app.register_blueprint(registrar_bp, url_prefix="/api/registrar")
app.register_blueprint(historial_bp, url_prefix="/api/historial")
app.register_blueprint(registradora_bp, url_prefix="/api/registradora")
app.register_blueprint(resumen_bp, url_prefix="/api/resumenGeneral")
app.register_blueprint(transacciones_bp, url_prefix="/api/transacciones")
app.register_blueprint(empleados_bp, url_prefix="/api/empleados")
app.register_blueprint(cambios_bp, url_prefix="/api/cambios")

if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 5000))
    #app.run(host="0.0.0.0", port=port)
    app.run()