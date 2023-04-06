from Receta import Receta
from Bbdd import Bbdd

bd = Bbdd()
import shutil
import spacy 
import re
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import pickle
import warnings
warnings.filterwarnings('once')


#Variables globales
Categorias = ["Aperitivos", "Carne", "Pasta", "Pescado", "Verdura"]
rutaListaParada = "ListaParada.txt"
rutaDiccionario = "DiccionarioL.txt"
rutaMatriz = "MatrizL.txt"

def leerFichero(rutaFichero):
    f = open(rutaFichero, 'r', encoding="utf-8")
    texto = f.read()
    f.close()
    return texto

def leerReceta():
    print()

def tokenizacion(texto):
    nlp = spacy.load('es_core_news_sm')
    doc = nlp(texto) # Crea un objeto de spacy tipo nlp
    tokens = [t.orth_ for t in doc] # Crea una lista con las palabras del texto
    return tokens

def tratamientoBasico(tokens):
    caracteres = "0123456789ºª!·$%&/()=|@#~€¬'?¡¿`+^*[]´¨}{,.-;:_<>\n \""
    listaTratada = []
    for token in tokens :
        for i in range (len(caracteres)):
            token = token.replace(caracteres[i],"")
        if(token != ""):
            listaTratada.append(token.lower())
    return listaTratada

def listaParada(tokens):
    listaParada = tratamientoBasico(tokenizacion(leerFichero(rutaListaParada)))
    listaDepurada = []
    for token in tokens:
        encontrado = False
        i=0
        while (encontrado==False and i<len(listaParada)):
            if (token==listaParada[i]):
                encontrado=True
            i+=1
        if encontrado==False and len(token)>2:
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

def tratarFichero(rutaReceta):
    tokens = tokenizacion(leerReceta(rutaReceta).texto)
    tokens = tratamientoBasico(tokens)
    tokens = listaParada(tokens)
    tokens = lematizacion(tokens)
    return tokens

def KNN():
    return KNeighborsClassifier(
        n_neighbors=16
    )

#Método para preparar los datos que usa el modelo
def prepararDatos():

    textosLeidos = leerFichero(rutaTextosTratados).splitlines()
    listaCategorias = []
    for ruta in textosLeidos:
        fichero = ruta.split('.')[0].split('/')[-1]
        categoria = re.sub("\d+", "", fichero)
        listaCategorias.append(Categorias.index(categoria))

    resultados = pd.DataFrame(listaCategorias)
    matriz = pd.DataFrame(rutaMatriz)    

    X = matriz.values
    y = resultados.values.ravel()
    
    return train_test_split(X, y, test_size=0.1, random_state=10)

#Método para importar un modelo
def cargarModelo(fichero):
    with open(fichero, 'rb') as f:
        modelo = pickle.load(f)
        f.close()
    return modelo

#Método para categorizar recetas nuevas
def categorizar(fichero, textos):
    resultado = []
    modelo = cargarModelo(fichero)
    diccionario = leerFichero(rutaDiccionario).splitlines()
    for elemento in os.listdir(textos):
        if re.search('.txt$', elemento):
            rutaReceta = textos+elemento
            filaNueva = np.zeros(len(diccionario))
            tokens = tratarFichero(rutaReceta)
            for token in tokens:
                if token in diccionario:
                    filaNueva[diccionario.index(token)] += 1
            categoria = Categorias[round(modelo.predict([filaNueva])[0])]
            ruta = textos + str(elemento)
            resultado.append(categoria)
            resultado.append(leerReceta(textos+elemento).titulo[:-1])
            resultado.append(str(elemento))
    print(resultado)
    return resultado


# Utilizaremos el diccionario, la matriz y la lista de parada de PC1, para mejorar dichos elementos tendríamos que modificar las
# funciones con las que los creamos:
'''
#Metodo para generar el diccionario
def generarDiccionario():
    diccionario = []
    ficherosTratados = []
    #Recorro todas las categorías
    for categoría in Categorias:
        rutaCategoría = './textos/'+categoría+'/'
        listaRecetas= os.listdir(rutaCategoría)
        #Recorro todas las recetas de cada categoría
        for receta in listaRecetas:
            #Compruebo si la receta no la había tratado ya
            recetaActual = '/textos/'+categoría+'/'+receta
            if recetaActual not in ficherosTratados:
                print(recetaActual)
                #Tratamiento de la receta
                tokens = tratarFichero('.'+recetaActual)
                #Compruebo si existe el token en la lista y sino lo añado al diccionario
                for token in tokens:
                    if token not in diccionario:
                        diccionario.append(token)
                    
                #Guardo la receta en los ficheros tratados para no volver a analizarla           
                ficherosTratados.append(recetaActual)
    #Guardo en ficheros el diccionaro y las noticias tratadas
    #Diccionario
    f = open(rutaDiccionario, "w", encoding="utf-8")
    for elemento in diccionario:
        f.write(elemento+"\n")
    f.close()

    #Noticias tratadas
    f = open(rutaTextosTratados, "w", encoding="utf-8")
    for elemento in ficherosTratados:
        f.write(elemento+"\n")
    f.close()
    
    return diccionario

#Metodos para generar la matriz
def generarFila(diccionario,rutaReceta):
    filaNueva = np.zeros(len(diccionario))
    tokens = tratarFichero(rutaReceta)
    for token in tokens:
        filaNueva[diccionario.index(token)] += 1
    return filaNueva

def generarMatriz():
    #leo el diccionario
    diccionario = leerFichero(rutaDiccionario).splitlines()
    #leo el fichero de las recetas tratadas
    recetas = leerFichero(rutaTextosTratados).splitlines()
    #Genero la nueva matriz
    matrizNueva = np.zeros((len(recetas), len(diccionario)), dtype=int)

    nFila = 0
    if os.path.isfile(rutaMatriz): #Si ya existe una matriz previa
        #Cargo la matriz antigua
        matriz = np.loadtxt(rutaMatriz)
        #Diferencia de longitud de cada fila entre la matriz antigua y nueva
        difLenRow = len(diccionario) - len(matriz[nFila])
        
        #Rellenamos de ceros las filas antiguas
        for fila in matriz:
            for i in range(difLenRow):
                fila = np.append(fila,0)
            matrizNueva[nFila] = fila
            nFila += 1

        #Guardamos las nuevas filas
        for i in range(len(recetas)-len(matriz)):
            filaNueva = generarFila(diccionario, os.getcwd()+recetas[len(matriz)+i])
            matrizNueva[len(matriz)+i] = filaNueva
    
    else:  # Si no existe una matriz previa
        #Guardamos las nuevas filas
        for receta in recetas:
            filaNueva=generarFila(diccionario, os.getcwd()+receta)
            matrizNueva[nFila] = filaNueva
            nFila += 1

    np.savetxt(rutaMatriz, matrizNueva, fmt='%i')
    return matrizNueva'''