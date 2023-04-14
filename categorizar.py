from Receta import Receta
import spacy
import numpy as np
import pickle
import warnings
nlp = spacy.load("es_core_news_sm")
warnings.filterwarnings('once')

rutaDiccionario = "ETL\DiccionarioL.txt"
rutaListaParada = "ETL\ListaParada.txt"
Categorias = ["Aperitivos", "Carne", "Pasta", "Pescado", "Verdura"]
rutaModelo = "ETL/KNN1.sav"

#Metodo para lectura de ficheros
def leerFichero(rutaFichero):
    f = open(rutaFichero, 'r', encoding="utf-8")
    texto = f.read()
    f.close()
    return texto

#Método para importar un modelo
def cargarModelo():
    with open(rutaModelo, 'rb') as f:
        modelo = pickle.load(f)
        f.close()
    return modelo

#Metodos de Tratamiento de ficheros
def tokenizacion(texto):
    nlp = spacy.load('es_core_news_sm')
    doc = nlp(texto)  # Crea un objeto de spacy tipo nlp
    # Crea una lista con las palabras del texto
    tokens = [t.orth_ for t in doc]
    return tokens

def tratamientoBasico(tokens):
    caracteres = "0123456789ºª!·$%&/()=|@#~€¬'?¡¿`+^*[]´¨}{,.-;:_<>\n \""
    listaTratada = []
    for token in tokens:
        for i in range(len(caracteres)):
            token = token.replace(caracteres[i], "")
        if(token != ""):
            listaTratada.append(token.lower())
    return listaTratada

def listaParada(tokens):
    listaParada = tratamientoBasico(tokenizacion(leerFichero(rutaListaParada)))
    listaDepurada = []
    for token in tokens:
        encontrado = False
        i = 0
        while (encontrado == False and i < len(listaParada)):
            if (token == listaParada[i]):
                encontrado = True
            i += 1
        if encontrado == False and len(token) > 2:
            listaDepurada.append(token)
    return listaDepurada

def lematizacion(tokens):
    nlp = spacy.load('es_core_news_sm')
    texto = ""
    for token in tokens:
        texto += token + " "
    doc = nlp(texto)
    lemmas = [tok.lemma_ for tok in doc]
    return lemmas

def tratarFichero(texto):
    tokens = tokenizacion(texto)
    tokens = tratamientoBasico(tokens)
    tokens = listaParada(tokens)
    tokens = lematizacion(tokens)
    return tokens

#Método para categorizar recetas nuevas
def categorizar(texto):
    modelo = cargarModelo()
    diccionario = leerFichero(rutaDiccionario).splitlines()
    filaNueva = np.zeros(len(diccionario))
    tokens = tratarFichero(texto)
    for token in tokens:
        if token in diccionario:
            filaNueva[diccionario.index(token)] += 1
    categoria = Categorias[round(modelo.predict([filaNueva])[0])]
    print(categoria)
    return categoria