# Esto simula lo que vendría de una base de datos
class Usuario:
    def __init__(self, id, nombre, email, edad):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.edad = edad

    def to_dict(self):
        """Convierte el objeto a diccionario para poder enviarlo como JSON"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "edad": self.edad
        }