# pip install mysql.connector
import mysql.connector

class Bbdd:
    db = ''
    cursor = ''

    def __init__(self):
        self.db = mysql.connector.connect(
            host="195.235.211.197",
            user="pc2_grupo4",
            passwd="Computacion.23",
            database="pc2_grupo4"
        )
        self.cursor = self.db.cursor()

    #Comprobar si un video ya existe en la base de datos
    def comprobarVideo(self, url):
        self.cursor.execute("SELECT * FROM Receta WHERE url=%s", (url,))
        consultaURL = self.cursor.fetchone()
        if consultaURL is None:
            return True
        else:
            return False 
    
    def insertarReceta(self, receta):
        sql = "INSERT INTO Receta (url, titulo, texto, categoria, comentarios, nutriscore, sentimiento, comentarios_positivos, comentarios_neutros, comentarios_negativos, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (receta.url, receta.titulo, receta.texto, receta.categoria, receta.comentarios, receta.nutriscore, receta.sentimiento, receta.c_positivo, receta.c_neutro, receta.c_negativo, receta.f_creacion)
        self.cursor.execute(sql, val)
        self.db.commit()
