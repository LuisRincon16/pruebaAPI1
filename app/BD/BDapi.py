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
        #------- para la registradora ---------
        self.crear_tabla_Ventas()
        self.crear_indices_ventas()

    def conectar(self):
        try:
            self.conexion = sqlitecloud.connect(self.url)
            return True
        except Exception as e:
            #print(f"Error al conectar a la base de datos: {e}")
            self.conexion = None
            return False

    def desconectar(self):
        if self.conexion:
            try:
                self.conexion.close()
                self.conexion = None
            except Exception as e:
                #print(f"Error al desconectar de la base de datos: {e}")
                self.conexion = None
                pass

    def crear_tablas(self, nombre_tabla=["compras", "gastos", "prestamos"]):
        try:
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
        except Exception as e:
            #print(f"Error al crear las tablas: {e}")
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

        conexion = self.conectar()
        if conexion:
            cursor = self.conexion.cursor()
            cursor.execute(f"INSERT INTO {nombre_tabla} (descripcion, valor, fecha, hora, tipo) VALUES (?, ?, ?, ?, ?)", (descripcion, valor, fecha, hora, tipo_ajustado))
            self.conexion.commit()
            self.desconectar()
            return True
        else:
            return False

    # --------- Vistas e índices para optimizar consultas del historial ---------

    def crear_vista_historial(self):
        try:
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
        except Exception as e:
            #print(f"Error al crear la vista del historial: {e}")
            self.desconectar()

    def crear_indice_fecha_hora(self):
        try:
            self.conectar()
            cursor = self.conexion.cursor()
            for table in ["compras", "gastos", "prestamos"]:
                cursor.execute(f"""CREATE INDEX IF NOT EXISTS
                                    idx_{table}_fecha_hora ON {table}(fecha, hora)""")
            self.conexion.commit()
            self.desconectar()
        except Exception as e:
            #print(f"Error al crear los índices de fecha y hora: {e}")
            self.desconectar()

    # --------- método para obtener datos del historial ---------

    def obtener_historial(self, fecha_inicio, fecha_fin, descripcion):
        result_conexion = self.conectar()
        if result_conexion:
            self.conexion.row_factory = sqlitecloud.Row
            cursor = self.conexion.cursor()
            if descripcion is None:
                cursor.execute("""SELECT * 
                                    FROM historial_completo
                                    WHERE fecha BETWEEN ? AND ?
                                    ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin))
            else:
                cursor.execute("""SELECT * 
                                    FROM historial_completo
                                    WHERE fecha BETWEEN ? AND ?
                                    AND descripcion LIKE ?
                                    ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin, f"%{descripcion}%"))
                
            datos = cursor.fetchall()
            self.desconectar()
            return [dict(row) for row in datos]
        else:
            return None
        

    def consultar_opciones(self, nombre_tabla):
        result_conexion = self.conectar()
        if result_conexion:
            cursor = self.conexion.cursor()
            cursor.execute(f"""SELECT DISTINCT descripcion 
                                FROM {nombre_tabla}""")
            datos = cursor.fetchall()
            self.desconectar()
            return [row[0] for row in datos]
        else:
            return None

    
    # --------- Métodos para la registradora ---------
    
    def crear_tabla_Ventas(self, nombre_tabla="ventas"):
        self.conectar()
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {nombre_tabla} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha VARCHAR NOT NULL,
                        hora VARCHAR NOT NULL,
                        monto INTEGER NOT NULL,
                        estado VARCHAR NOT NULL
                    )
                """)
                self.conexion.commit()
                self.desconectar()
            except Exception as e:
                #print(f"Error al crear la tabla: {e}")
                self.desconectar()
    
    def crear_indices_ventas(self):
        self.conectar()
        if self.conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_fecha_hora_ventas
                    ON ventas(fecha, hora)
                """)
                self.conexion.commit()
                self.desconectar()
            except Exception as e:
                #print(f"Error al crear los índices: {e}")
                self.desconectar()

    def agregar_venta(self, fecha, hora, monto, estado):
        result_conexion = self.conectar()
        if result_conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("INSERT INTO ventas (fecha, hora, monto, estado) VALUES (?, ?, ?, ?)", (fecha, hora, monto, estado))
                self.conexion.commit()
                self.desconectar()
                return True
            except Exception as e:
                #print(f"Error al agregar la venta: {e}")
                self.desconectar()
                return False
        else:
            return False
        
    def consultar_ventas(self, fecha_inicio, fecha_fin):
        result_conexion = self.conectar()
        if result_conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("""SELECT * 
                                    FROM ventas
                                    WHERE fecha BETWEEN ? AND ?
                                    ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin))
                datos = cursor.fetchall()
                self.desconectar()
                return datos
            except Exception as e:
                #print(f"Error al consultar las ventas: {e}")
                self.desconectar()
                return None
        else:
            return None
        
    def consultar_venta_por_id(self, id_venta):
        result_conexion = self.conectar()
        if result_conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("SELECT * FROM ventas WHERE id = ?", (id_venta,))
                dato = cursor.fetchone()
                self.desconectar()
                if dato is None:
                    return False
                return dato
            except Exception as e:
                #print(f"Error al consultar la venta por ID: {e}")
                self.desconectar()
                return None
        else:
            return None
        
    def total_vendido(self, fecha_inicio, fecha_fin):
        result_conexion = self.conectar()
        if result_conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("""SELECT SUM(monto)
                                    FROM ventas
                                    WHERE fecha BETWEEN ? AND ?""", (fecha_inicio, fecha_fin))
                resultado = cursor.fetchone()
                self.desconectar()
                if resultado is None:
                    return False
                return resultado
            except Exception as e:
                #print(f"Error al calcular el total vendido: {e}")
                self.desconectar()
                return None
        else:
            return None
    
    def eliminar_venta_por_id(self, id_venta):
        result_conexion = self.conectar()
        if result_conexion:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("DELETE FROM ventas WHERE id = ?", (id_venta,))
                self.conexion.commit()
                self.desconectar()
                return True
            except Exception as e:
                #print(f"Error al eliminar la venta por ID: {e}")
                self.desconectar()
                return False
        else:
            return False
    
    def agregar_ventas_pendientes(self, ventas_pendientes):
        result_conexion = self.conectar()
        if result_conexion:
            try:
                cursor = self.conexion.cursor()
                for venta in ventas_pendientes:
                    fecha, hora, monto = venta
                    cursor.execute("INSERT INTO ventas (fecha, hora, monto, estado) VALUES (?, ?, ?, ?)", (fecha, hora, monto, "ACTUALIZADO"))
                self.conexion.commit()
                self.desconectar()
                return True
            except Exception as e:
                #print(f"Error al agregar las ventas pendientes: {e}")
                self.desconectar()
                return False
        else:
            return False