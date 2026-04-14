from datetime import datetime
import sqlitecloud
from dotenv import load_dotenv
import os
import pytz

load_dotenv()

class BaseDeDatos():
    def __init__(self):
        #base_dir = os.path.dirname(os.path.abspath(__file__))
        #self.nombre_bd = os.path.join(base_dir, "db", nombre_bd)
        self.conexion = None
        self.url = os.getenv("SQLITECLOUD_URL")
        self.zonaHorariaColombia = pytz.timezone("America/Bogota")
        self.crear_tablas()
        self.crear_vista_historial()
        self.crear_indice_fecha_hora()

    def conectar(self):
        self.conexion = sqlitecloud.connect(self.url)

    def desconectar(self):
        if self.conexion:
            self.conexion.close()
            self.conexion = None

    def crear_tablas(self, nombre_tabla=["compras", "gastos", "prestamos"]):
        self.conectar()
        cursor = self.conexion.cursor()
        for table in nombre_tabla:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descripcion VARCHAR NOT NULL,
                    valor INTEGER NOT NULL,
                    fecha VARCHAR NOT NULL,
                    hora VARCHAR NOT NULL,
                    tipo VARCHAR NOT NULL )""")
        self.conexion.commit()
        self.desconectar()

    def agregar_dato(self, nombre_tabla, descripcion, valor):
        ahora = datetime.now(self.zonaHorariaColombia)
        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")

        #print(f"\nAgregando a {nombre_tabla}: {descripcion} - {valor} el {fecha} a las {hora}\n")
        tipo_ajustado = None
        if nombre_tabla == "COMPRAS":
            tipo_ajustado = "Com."
        elif nombre_tabla == "GASTOS":
            tipo_ajustado = "Gas."
        elif nombre_tabla == "PRESTAMOS":
            tipo_ajustado = "Pres."

        self.conectar()
        cursor = self.conexion.cursor()
        cursor.execute(f"INSERT INTO {nombre_tabla} (descripcion, valor, fecha, hora, tipo) VALUES (?, ?, ?, ?, ?)", (descripcion, valor, fecha, hora, tipo_ajustado))
        self.conexion.commit()
        self.desconectar()

    # --------- Vistas e índices para optimizar consultas del historial ---------

    def crear_vista_historial(self):
        self.conectar()
        cursor = self.conexion.cursor()
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS historial_completo AS
            SELECT * FROM compras
            UNION ALL
            SELECT * FROM gastos
            UNION ALL
            SELECT * FROM prestamos
        """)
        self.conexion.commit()
        self.desconectar()

    def crear_indice_fecha_hora(self):
        self.conectar()
        cursor = self.conexion.cursor()
        for table in ["compras", "gastos", "prestamos"]:
            cursor.execute(f"""CREATE INDEX IF NOT EXISTS
                                idx_{table}_fecha_hora ON {table}(fecha, hora)""")
        self.conexion.commit()
        self.desconectar()

    # --------- método para obtener datos del historial ---------

    def obtener_historial(self, fecha_inicio, fecha_fin):
        self.conectar()

        self.conexion.row_factory = sqlitecloud.Row

        cursor = self.conexion.cursor()
        cursor.execute("""SELECT * 
                            FROM historial_completo
                            WHERE fecha BETWEEN ? AND ?
                            ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin))
        datos = cursor.fetchall()
        self.desconectar()

        return [dict(row) for row in datos]