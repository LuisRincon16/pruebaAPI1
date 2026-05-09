from datetime import datetime
import sqlitecloud
import os
import pytz

class BaseDeDatos():
    def __init__(self):
        self.url = os.getenv("SQLITECLOUD_URL")
        self.zonaHorariaColombia = pytz.timezone("America/Bogota")
        self.cuentasBancarias = {"NEQUI", "DAVIPLATA"}
        self.empleados = {"ANDRES", "SERGIO", "GUILLE"}
        self.crear_tablas()
        self.crear_indices()
        #------- vistas para optimizar consultas del resumen general ---------
        self.crear_vista_historial()
        self.crear_vista_total_gastado()

    def crear_tablas(self):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            for table in ["compras", "gastos", "prestamos"]:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        descripcion VARCHAR NOT NULL,
                        valor INTEGER NOT NULL,
                        fecha VARCHAR NOT NULL,
                        hora VARCHAR NOT NULL,
                        tipo VARCHAR NOT NULL )""")
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha VARCHAR NOT NULL,
                    hora VARCHAR NOT NULL,
                    monto INTEGER NOT NULL,
                    estado VARCHAR NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transacciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descripcion VARCHAR NOT NULL,
                    valor INTEGER NOT NULL,
                    fecha VARCHAR NOT NULL,
                    hora VARCHAR NOT NULL, 
                    tipo VARCHAR NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prestamos_emp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descripcion VARCHAR NOT NULL,
                    valor INTEGER NOT NULL,
                    fecha VARCHAR NOT NULL,
                    hora VARCHAR NOT NULL,
                    tipo VARCHAR NOT NULL
                )
            """)
            conexion.commit()
        except Exception as e:
            pass
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
    
    def crear_indices(self):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            for table in ["compras", "gastos", "prestamos", "ventas"]:     #indices para compras, gastos, prestamos y ventas
                cursor.execute(f"""CREATE INDEX IF NOT EXISTS idx_fecha_hora_{table}
                                    ON {table}(fecha, hora)""")
            for table2 in ["transacciones", "prestamos_emp"]:              #indices para transacciones y prestamos_emp
                cursor.execute(f"""CREATE INDEX IF NOT EXISTS idx_tipo_fecha_{table2}
                                    ON {table2}(tipo, fecha)""")
            conexion.commit()
        except Exception as e:
            pass
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
    
    def crear_vista_historial(self):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS historial_completo AS
                SELECT * FROM compras
                UNION ALL
                SELECT * FROM gastos
                UNION ALL
                SELECT * FROM prestamos
            """)
            conexion.commit()
        except Exception as e:
            pass
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def crear_vista_total_gastado(self):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS total_gastado AS
                SELECT fecha, SUM(valor) AS total
                FROM(
                    SELECT fecha, valor FROM compras
                    UNION ALL
                    SELECT fecha, valor FROM gastos
                    UNION ALL
                    SELECT fecha, valor FROM prestamos)
                GROUP BY fecha
            """)
            conexion.commit()
        except Exception as e:
            pass
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def agregar_dato(self, nombre_tabla, descripcion, valor):
        ahora = datetime.now(self.zonaHorariaColombia)
        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")

        tipo_ajustado = None
        if nombre_tabla == "COMPRAS":
            tipo_ajustado = "C"
        elif nombre_tabla == "GASTOS":
            tipo_ajustado = "G"
        elif nombre_tabla == "PRESTAMOS":
            tipo_ajustado = "P"

        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute(f"INSERT INTO {nombre_tabla} (descripcion, valor, fecha, hora, tipo) VALUES (?, ?, ?, ?, ?)", (descripcion, valor, fecha, hora, tipo_ajustado))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:        
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
    
    # --------- método para obtener datos del historial ---------

    def obtener_historial(self, fecha_inicio, fecha_fin, descripcion):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            conexion.row_factory = sqlitecloud.Row
            cursor = conexion.cursor()
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
            return [dict(row) for row in datos]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
        
    def consultar_opciones(self, nombre_tabla):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute(f"""SELECT DISTINCT descripcion 
                                FROM {nombre_tabla}""")
            datos = cursor.fetchall()
            return [row[0] for row in datos]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def obtener_resumen_general(self, fecha_inicio, fecha_fin, nombre_tabla):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            conexion.row_factory = sqlitecloud.Row
            cursor = conexion.cursor()
            if nombre_tabla in self.cuentasBancarias:
                cursor.execute(f"""SELECT *
                                FROM transacciones
                                WHERE fecha BETWEEN ? AND ? AND tipo = ?
                                ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin, nombre_tabla))
            elif nombre_tabla in self.empleados:
                cursor.execute(f"""SELECT *
                                FROM prestamos_emp
                                WHERE fecha BETWEEN ? AND ? AND tipo = ?
                                ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin, nombre_tabla))
            else:
                cursor.execute(f"""SELECT *
                                    FROM {nombre_tabla}
                                    WHERE fecha BETWEEN ? AND ?
                                    ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin))
            datos = cursor.fetchall()
            #print(f"\nresumen antes del endpoint: {datos}")
            return [dict(row) for row in datos]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
        
    def obtener_totales_por_fecha(self, fecha_inicio, fecha_fin, nombre_tabla):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            if nombre_tabla in self.cuentasBancarias:
                cursor.execute(f"""SELECT SUM(valor) AS total
                                FROM transacciones
                                WHERE fecha BETWEEN ? AND ? AND tipo = ? """, (fecha_inicio, fecha_fin, nombre_tabla))
            elif nombre_tabla in self.empleados:
                cursor.execute(f"""SELECT SUM(valor) AS total
                                FROM prestamos_emp
                                WHERE fecha BETWEEN ? AND ? AND tipo = ? """, (fecha_inicio, fecha_fin, nombre_tabla))
            else:
                cursor.execute(f"""SELECT SUM(valor) AS total
                                    FROM {nombre_tabla}
                                    WHERE fecha BETWEEN ? AND ?""", (fecha_inicio, fecha_fin))
            datos = cursor.fetchone()
            if datos[0] is None:
                return 0
            return datos[0]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def obtener_acumulado(self, fecha_inicio_formateada, fecha_final_formateada, nombre_tabla):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            if nombre_tabla in self.cuentasBancarias:
                cursor.execute(f"""SELECT SUM(valor) AS total
                                FROM transacciones
                                WHERE fecha >= ? AND fecha < ? AND tipo = ? """, (fecha_inicio_formateada, fecha_final_formateada, nombre_tabla))
            elif nombre_tabla in self.empleados:
                cursor.execute(f"""SELECT SUM(valor) AS total
                                FROM prestamos_emp
                                WHERE fecha >= ? AND fecha < ? AND tipo = ? """, (fecha_inicio_formateada, fecha_final_formateada, nombre_tabla))
            else:
                cursor.execute(f"""SELECT SUM(valor) AS total
                                    FROM {nombre_tabla}
                                    WHERE fecha >= ? AND fecha < ?""", (fecha_inicio_formateada, fecha_final_formateada))
            datos = cursor.fetchone()
            if datos[0] is None:
                return 0
            return datos[0]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def obtener_total_ventas(self, fecha_inicio, fecha_fin):     #Devuelve el total de VENTAS
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""SELECT SUM(monto) AS total
                                FROM ventas
                                WHERE fecha BETWEEN ? AND ?""", (fecha_inicio, fecha_fin))
            datos = cursor.fetchone()
            if datos[0] is None:
                return 0
            return datos[0]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def obtener_acumulado_ventas(self, fecha_inicio_formateada, fecha_final_formateada):     #Devuelve el acumulado de ventas en el mes proporcionado
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""SELECT SUM(monto) AS total
                                FROM ventas
                                WHERE fecha >= ? AND fecha < ?""", (fecha_inicio_formateada, fecha_final_formateada))
            datos = cursor.fetchone()
            if datos[0] is None:
                return 0
            return datos[0]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def obtener_total_gastado(self, fecha_inicio, fecha_fin):  #Devuelve el total gastado (para restarlo al vendido y obtener el efectivo)
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""SELECT SUM(total)
                            FROM total_gastado
                            WHERE fecha BETWEEN ? AND ?""", (fecha_inicio, fecha_fin))
            resultado = cursor.fetchone()
            if resultado[0] is None:
                return 0
            return resultado[0]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def obtener_acumulado_total_gastado(self, fecha_inicio_formateada, fecha_final_formateada): #Devuelve el acumulado de lo gastado en el mes proporcionado (para restarlo al acumulado de ventas y obtener el efectivo acumulado)
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""SELECT SUM(total)
                           FROM total_gastado
                           WHERE fecha >= ? AND fecha < ?""", (fecha_inicio_formateada, fecha_final_formateada))
            resultado = cursor.fetchone()
            if resultado[0] is None:
                return 0
            return resultado[0]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    # --------- Métodos para la registradora ---------
    def agregar_venta(self, fecha, hora, monto, estado):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO ventas (fecha, hora, monto, estado) VALUES (?, ?, ?, ?)", (fecha, hora, monto, estado))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
        
    def consultar_ventas(self, fecha_inicio, fecha_fin):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""SELECT * 
                                FROM ventas
                                WHERE fecha BETWEEN ? AND ?
                                ORDER BY fecha DESC, hora DESC""", (fecha_inicio, fecha_fin))
            datos = cursor.fetchall()
            return datos
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
        
    def consultar_venta_por_id(self, id_venta):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ventas WHERE id = ?", (id_venta,))
            dato = cursor.fetchone()
            if dato is None:
                return False
            return dato
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
        
    def total_vendido(self, fecha_inicio, fecha_fin):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("""SELECT SUM(monto)
                                FROM ventas
                                WHERE fecha BETWEEN ? AND ?""", (fecha_inicio, fecha_fin))
            resultado = cursor.fetchone()
            if resultado[0] is None:
                return 0
            return resultado[0]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
    
    def eliminar_venta_por_id(self, id_venta):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM ventas WHERE id = ?", (id_venta,))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass
    
    def agregar_ventas_pendientes(self, ventas_pendientes):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            for venta in ventas_pendientes:
                fecha, hora, monto = venta
                cursor.execute("INSERT INTO ventas (fecha, hora, monto, estado) VALUES (?, ?, ?, ?)", (fecha, hora, monto, "ACTUALIZADO"))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def recibir_transaccion(self, descripcion, valor, tipo):
        ahora = datetime.now(self.zonaHorariaColombia)
        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO transacciones (descripcion, valor, fecha, hora, tipo) VALUES (?, ?, ?, ?, ?)", (descripcion, valor, fecha, hora, tipo))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def registrar_prestamo_emp(self, descripcion, valor, empleado):
        ahora = datetime.now(self.zonaHorariaColombia)
        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO prestamos_emp (descripcion, valor, fecha, hora, tipo) VALUES (?, ?, ?, ?, ?)", (descripcion, valor, fecha, hora, empleado))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def obtener_historial_diario_emp(self, dia_a_consultar):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            conexion.row_factory = sqlitecloud.Row
            cursor = conexion.cursor()
            cursor.execute("""SELECT *
                                FROM prestamos_emp
                                WHERE fecha = ? 
                                ORDER BY fecha DESC, hora DESC""", (dia_a_consultar,))
            datos = cursor.fetchall()
            return [dict(row) for row in datos]
        except Exception as e:
            return None
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def eliminar_registro(self, id, tipo):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            if tipo in self.empleados:
                cursor.execute("DELETE FROM prestamos_emp WHERE id = ?", (id,))
            else:
                cursor.execute(f"DELETE FROM {tipo} WHERE id = ?", (id,))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass

    def actualizar_registro(self, id, tipo, descripcion, valor):
        conexion = None
        try:
            conexion = sqlitecloud.connect(self.url)
            cursor = conexion.cursor()
            if tipo in self.empleados:
                cursor.execute("""UPDATE prestamos_emp
                                SET descripcion = ?, valor = ?
                                WHERE id = ?""", (descripcion, valor, id))
            else:
                cursor.execute(f"""UPDATE {tipo}
                               SET descripcion = ?, valor = ?
                               WHERE id = ?""", (descripcion, valor, id))
            conexion.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conexion:
                try:
                    conexion.close()
                except Exception as e:
                    pass