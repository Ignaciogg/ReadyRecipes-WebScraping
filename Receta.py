import datetime


class Receta:
    url = ""
    titulo = ""
    texto = ""
    categoria = ""
    nutriscore = ""
    comentarios = 0
    sentimiento = 0.0
    c_positivo = 0
    c_neutro = 0
    c_negativo = 0
    f_creacion = ""

    def __init__(self, url):
        self.url = url
        self.f_creacion = datetime.datetime.now().strftime("%Y-%m-%d")

    def toString(self):
        return (
            "url: " + str(self.url) + 
            "\ntitulo: " + str(self.titulo) +
            "\ntexto: " + str(self.texto) +
            "\ncategoria: " + str(self.categoria) +
            "\nnutriscore: " + str(self.nutriscore) +
            "\ncomentarios: " + str(self.comentarios) +
            "\nsentimiento: " + str(self.sentimiento) +
            "\nfecha creacion: " + str(self.f_creacion) +
            "\ncomentarios positivos: " + str(self.c_positivo) +
            "\ncomentarios neutros: " + str(self.c_neutro) +
            "\ncomentarios negativos: " + str(self.c_negativo)
        )