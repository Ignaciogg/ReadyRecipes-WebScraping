# pip install google-api-python-client
# pip install pytube
# pip install SpeechRecognition
# pip install textblob
# pip install googletrans==4.0.0-rc1

import warnings
import urllib.request
import json
import os
import re
from textblob import TextBlob
from googletrans import Translator
from googleapiclient.discovery import build
from Receta import Receta, RecetaEncoder
from Bbdd import Bbdd
from webscraping_ingredientes import buscar_ingredientes
from webscraping_nutriscore import obtener_nutriscore
warnings.filterwarnings('ignore')

categoria = 'Verdura'
ruta = f'Textos/{categoria}'

maxComents = 1000
bd = Bbdd()
urlReceta = "http://127.0.0.1:8000/api/nuevaReceta"
urlIngrediente = "http://127.0.0.1:8000/api/nuevoIngrediente"

#Borrar si existe algun fichero descargado anteriormente
def borrarficheros():
    os.remove('receta.mp4') if os.path.exists('receta.mp4') else None
    os.remove('receta.wav') if os.path.exists('receta.wav') else None

#Traducir un texto al ingles
def traducir(texto):
    try:
        trans = Translator()
        trans_sen = trans.translate(texto,dest='en')
	    #sleep(0.1)
        return trans_sen.text
    except:
        return texto
	
#Analisis de sentimiento de un texto
def analisisSentimiento(texto):
    sentimiento = TextBlob(traducir(texto)).sentiment.polarity
    return sentimiento

#Metedo para obtener un objeto para poder lanzar request a la api de youtube
def getYoutube():
    DEVELOPER_KEY = "AIzaSyB0Z5YoVzZPgH1EOSVFJAL5X8EBb9qbSPU"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey = DEVELOPER_KEY)
    return youtube_object

#Metodo para obtener los comentarios de un video
def obtenerComentarios(video_id):
    youtube=getYoutube()
    
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=maxComents
    )
    response = request.execute()
    return response

# 1. EXTRAER X URLs DE UN CANAL DE YOUTUBE
listaVideos = os.listdir(ruta)
for video in listaVideos: #Recorremos todos los videos

    try:
        rutaReceta = ruta + '/' + video
        with open(rutaReceta, 'r', encoding='utf-8') as archivo:
            fichero = archivo.readlines()
            video_url = fichero[0]
            titulo = fichero[1]
            texto = fichero[3]
            
        video_id = video_url.replace('https://www.youtube.com/watch?v=', '')
        video_url_enmbed = f"https://www.youtube.com/embed/{video_id}"
    except:
        print("Error al obtener la url del video: ")
        continue
        
    # 2. COMPROBAR SI YA TENEMOS ESTA URL
    if not bd.comprobarVideo(video_url_enmbed):
        print('Ya tenemos esta receta')
        continue

    # 3. EXTRAER LA TRANSCRIPCION DE ESTA RECETA
    try:
        receta = Receta(video_url_enmbed)
        borrarficheros()
        receta.texto = texto
    except:
        print("Error al transcribir el video: ", video_url)
        continue
    
    # 4. EXTRAER LOS COMENTARIOS DE ESTE VIDEO
    try:
        print(video_id)
        listaComentarios = obtenerComentarios(video_id)
        comentarios = []
        sentimientoAcumulado = 0
        for comentario in listaComentarios['items']:
            comment = comentario['snippet']['topLevelComment']
            texto = comment['snippet']['textDisplay']
            texto = re.sub('[^\w\s#@/:%.,_-]', '', texto, flags=re.UNICODE)
            sentimiento = analisisSentimiento(str(texto))
            sentimientoAcumulado+=sentimiento
            if sentimiento < 0:
                receta.c_negativo+=1
            elif sentimiento > 0:
                receta.c_positivo+=1
            else:
                receta.c_neutro+=1
            comentarios.append(texto)
        receta.comentarios = len(comentarios)
        receta.sentimiento = ((sentimientoAcumulado/receta.comentarios)+1) / 2 * 100
    except:
        print("Error al obtener los comentarios del video: ", video_url)
        continue
    
    # 5. AÑADIMOS MÁS ATRIBUTOS
    try:
        receta.titulo = titulo
        listaIngredientes = buscar_ingredientes(receta.texto)
        receta.nutriscore = obtener_nutriscore(listaIngredientes)
        receta.categoria = categoria 
    except:
        print("Error al obtener los atributos del video: ", video_url)
        continue
    # 6. INSERTAMOS EN LA BASE DE DATOS
    try:
        receta_json = json.dumps(receta.to_dict(), cls=RecetaEncoder)
        receta_json = receta_json.encode('utf-8')

        req = urllib.request.Request(urlReceta, receta_json)
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req)
        response_text = response.read().decode('utf-8')
        response_text = json.loads(response_text)
        receta.id = response_text['id']
        print("id: ", receta.id)
        for ingrediente in listaIngredientes:
            ingrediente = {"nombre": ingrediente, "id_Receta": receta.id}
            ingrediente_json = json.dumps(ingrediente).encode('utf-8')
            print(ingrediente_json)
            req = urllib.request.Request(urlIngrediente, ingrediente_json)
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            response_text = response.read().decode('utf-8')
            response_text = json.loads(response_text)
            print(response_text)
    except:
        print("Error al insertar la receta en la base de datos: ", video_url)
        continue

    print("Receta insertada correctamente: ")
    