from datetime import datetime
import sqlitecloud
from dotenv import load_dotenv
import os

load_dotenv()

class BaseDeDatos():
    def __init__(self):
        #base_dir = os.path.dirname(os.path.abspath(__file__))
        #self.nombre_bd = os.path.join(base_dir, "db", nombre_bd)
        self.conexion = None
        self.url = os.getenv("SQLITECLOUD_URL")
        self.crear_tabla()

    def conectar(self):
        self.conexion = sqlitecloud.connect(self.url)

    def desconectar(self):
        if self.conexion:
            self.conexion.close()
            self.conexion = None

    def crear_tabla(self, nombre_tabla=["compras", "gastos", "prestamos"]):
        self.conectar()
        cursor = self.conexion.cursor()
        for table in nombre_tabla:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descripcion VARCHAR NOT NULL,
                    valor INTEGER NOT NULL,
                    fecha VARCHAR NOT NULL,
                    hora VARCHAR NOT NULL) """)
        self.conexion.commit()
        self.desconectar()

    def agregar_dato(self, nombre_tabla, descripcion, valor):
        fecha = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M:%S")

        #print(f"\nAgregando a {nombre_tabla}: {descripcion} - {valor} el {fecha} a las {hora}\n")

        self.conectar()
        cursor = self.conexion.cursor()
        cursor.execute(f"INSERT INTO {nombre_tabla} (descripcion, valor, fecha, hora) VALUES (?, ?, ?, ?)", (descripcion, valor, fecha, hora))
        self.conexion.commit()
        self.desconectar()