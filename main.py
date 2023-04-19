# pip install google-api-python-client
# pip install pytube
# pip install SpeechRecognition
# pip install textblob
# pip install googletrans==4.0.0-rc1

import warnings
from pytube import YouTube
import urllib.request
import json
import os
import re
import speech_recognition as sr
from textblob import TextBlob
from googletrans import Translator
from time import sleep
from ffmpy import FFmpeg
from googleapiclient.discovery import build
from categorizar import categorizar
from Receta import Receta, RecetaEncoder
from Bbdd import Bbdd
from webscraping_ingredientes import buscar_ingredientes
from webscraping_nutriscore import obtener_nutriscore
warnings.filterwarnings('ignore')

maxVideos = 1000
maxComents = 1000
bd = Bbdd()
urlReceta = "http://127.0.0.1:8000/api/nuevaReceta"
urlIngrediente = "http://127.0.0.1:8000/api/nuevoIngrediente"

#Descargar video desde una url
def descargarVideo(url):
    yt = YouTube(url)
    t = yt.streams.filter(only_audio=True).first()
    nombre = 'receta'
    t.download('./', nombre+'.mp4')
    convertirAudio(nombre)
    try:
        return transcribirAudio(nombre)
    except:
        print('ERROR. Audio mayor 10MB')
        os.remove(nombre+'.wav')

#Convertir video a audio
def convertirAudio(nombre):
    rutaEntrada = nombre+'.mp4'
    rutaSalida = nombre+'.wav'

    with open(os.devnull, 'w') as devnull:
        ff = FFmpeg(executable='C:\\ffmpeg\\bin\\ffmpeg.exe',
        inputs ={rutaEntrada: None},
        outputs ={rutaSalida: None})
        ff.run(stdout=devnull, stderr=devnull)

    try:
        os.remove(rutaEntrada)
    except:
        print("No se puede borrar vídeo")

#Transcribir audio a texto
def transcribirAudio(nombre):
    ruta = nombre+'.wav'
    with open(os.devnull, 'w') as devnull:
        # Iniciamos reconocimiento de voz
        re = sr.Recognizer()
        # Conversion audio-texto
        with sr.AudioFile(ruta) as source:
            info_audio = re.record(source)
            texto = re.recognize_google(info_audio, language="es-ES", show_all=False, key=None)
    try:
        os.remove(ruta)
    except:
        print("No se puede borrar audio")  
    return texto

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

#Metodo para a traves de un link de un video, obtener una lista de videos de ese canal
def obtenerVideos(url):
    yt = YouTube(url)
    channel_id = yt.channel_id
    
    youtube=getYoutube()
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=maxVideos
    )
    response = request.execute()
    return response

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
superGustoso = 'https://www.youtube.com/watch?v=zfD0C3_gl7Q'
listaVideos = obtenerVideos(superGustoso)

for video in listaVideos["items"]: #Recorremos todos los videos
    try:
        video_id = video["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_url_enmbed = f"https://www.youtube.com/embed/{video_id}"
        # 2. COMPROBAR SI YA TENEMOS ESTA URL
        if not bd.comprobarVideo(video_url_enmbed):
            continue

        # 3. EXTRAER LA TRANSCRIPCION DE ESTA RECETA
        receta = Receta(video_url_enmbed)
        borrarficheros()
        receta.texto = descargarVideo(video_url)
        
        # 4. EXTRAER LOS COMENTARIOS DE ESTE VIDEO
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
        
        # 5. AÑADIMOS MÁS ATRIBUTOS
        receta.titulo = video['snippet']['title']
        listaIngredientes = buscar_ingredientes(receta.texto)
        receta.nutriscore = obtener_nutriscore(listaIngredientes)
        receta.categoria = categorizar(receta.texto) 
        # 6. INSERTAMOS EN LA BASE DE DATOS
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

        print("Receta insertada correctamente: ")
    except:
        print("Error al procesar el video: ", video_url)
        continue
    
