import datetime

class Receta():
    url = ''
    titulo = ''
    texto = ''
    categoria = ''
    nutriscore = ''
    comentarios = 0
    sentimiento = 0.0
    c_positivo = 0
    c_neutro = 0
    c_negativo = 0
    f_creacion = ''

    def __init__(self,url):
        self.url = url
        self.f_creacion = datetime.datetime.now().strftime('%Y-%m-%d')
    
    def toString(self):
        print(self.url)
        print(self.titulo)
        print(self.texto)
        print(self.categoria)
        print(self.nutriscore)
        print(self.comentarios)
        print(self.sentimiento)
        print(self.c_positivo)
        print(self.c_neutro)
        print(self.c_negativo)
        print(self.f_creacion)
    