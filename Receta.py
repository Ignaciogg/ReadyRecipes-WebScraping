import datetime


class Receta:
    url = ""
    titulo = "prueba"
    texto = ""
    categoria = "Sin asignar"
    nutriscore = 0.0
    comentarios = 0
    sentimiento = 0.0
    c_positivo = 0
    c_neutro = 0
    c_negativo = 0
    f_creacion = ""
    f_modificacion = ""
    f_eliminacion = ""

    def __init__(self, url):
        self.url = url
        self.f_creacion = datetime.datetime.now().strftime("%Y-%m-%d")

    def toString(self):
        return ("url: " + str(self.url) +
                "\ntitulo: " + str(self.titulo) +
                "\ntexto: " + str(self.texto) +
                "\ncategoria: " + str(self.categoria) +
                "\nnutriscore: " + str(self.nutriscore) +
                "\ncomentarios: " + str(self.comentarios) +
                "\nsentimiento: " + str(self.sentimiento) +
                "\ncomentarios positivos: " + str(self.c_positivo) +
                "\ncomentarios neutros: " + str(self.c_neutro) +
                "\ncomentarios negativos: " + str(self.c_negativo) +
                "\nfecha creacion: " + str(self.f_creacion) +
                "\nfecha modificacion: " + str(self.f_modificacion) +
                "\nfecha eliminacion: " + str(self.f_eliminacion)
        )