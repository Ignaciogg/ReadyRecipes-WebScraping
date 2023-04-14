import json
import datetime

class Receta:
    def __init__(self, url):
        self.url = url
        self.titulo = "prueba"
        self.texto = ""
        self.categoria = "Sin asignar"
        self.nutriscore = 0.0
        self.comentarios = 0
        self.sentimiento = 0.0
        self.c_positivo = 0
        self.c_neutro = 0
        self.c_negativo = 0
        self.f_creacion = None
        self.f_modificacion = None
        self.f_eliminacion = None

    def to_dict(self):
        return {
            "url": self.url,
            "titulo": self.titulo,
            "texto": self.texto,
            "categoria": self.categoria,
            "nutriscore": self.nutriscore,
            "comentarios": self.comentarios,
            "sentimiento": self.sentimiento,
            "comentarios_positivos": self.c_positivo,
            "comentarios_neutros": self.c_neutro,
            "comentarios_negativos": self.c_negativo,
            "f_creacion": self.f_creacion,
            "f_modificacion": self.f_modificacion,
            "f_eliminacion": self.f_eliminacion
        }

class RecetaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
