# pip install google-api-python-client
# pip install pytube
# pip install SpeechRecognition
# pip install textblob
# pip install googletrans==4.0.0-rc1

from pytube import YouTube
import os
import re
import speech_recognition as sr
from textblob import TextBlob
from googletrans import Translator
from time import sleep
from ffmpy import FFmpeg
from googleapiclient.discovery import build

from Receta import Receta
from Bbdd import Bbdd
from webscraping_nutriscore import obtener_nutriscore
#from webscraping_ingredientes import *

maxVideos = 1
maxComents = 50
bd = Bbdd()

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

    ff = FFmpeg(executable='C:\\ffmpeg\\bin\\ffmpeg.exe',
    inputs ={rutaEntrada: None},
    outputs ={rutaSalida: None})
    ff.run()
    try:
        os.remove(rutaEntrada)
    except:
        print("No se puede borrar vídeo")

#Transcribir audio a texto
def transcribirAudio(nombre):
    ruta = nombre+'.wav'
    #iniciamos reconocimiento de voz
    re = sr.Recognizer()
    #conversion audio-texto
    with sr.AudioFile(ruta) as source:
        info_audio = re.record(source)
        texto = re.recognize_google(info_audio, language="es-ES")
    try:
        os.remove(ruta)
    except:
        print("No se puede borrar audio")
    return texto

#Traducir un texto al ingles
def traducir(texto):
	trans = Translator()
	trans_sen = trans.translate(texto,dest='en')
	sleep(0.1)
	return trans_sen.text

#Analisis de sentimiento de un texto
def analisisSentimiento(texto):
    sentimiento = TextBlob(traducir(texto)).sentiment.polarity
    return sentimiento

#Metedo para obtener un objeto para poder lanzar request a la api de youtube
def get_youtube():
    DEVELOPER_KEY = "AIzaSyB0Z5YoVzZPgH1EOSVFJAL5X8EBb9qbSPU"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey = DEVELOPER_KEY)
    return youtube_object

#Metodo para a traves de un link de un video, obtener una lista de videos de ese canal
def obtenerVideos(url):
    yt = YouTube(url)
    channel_id = yt.channel_id
    
    youtube=get_youtube()
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,  # Reemplaza con el ID del canal que deseas obtener los videos
        maxResults=maxVideos
    )
    response = request.execute()
    return response

#Metodo para obtener los comentarios de un video
def obtenerComentarios(video_id):
    youtube=get_youtube()
    
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
    
    video_id = video["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # 2. COMPROBAR SI YA TENEMOS ESTA URL
    if not bd.comprobarVideo(video_url):
        continue

    # 3. EXTRAER LA TRANSCRIPCION DE ESTA RECETA
    receta = Receta(video_url)
    receta.titulo = video['snippet']['title']
    receta.texto = descargarVideo(video_url)
    
    # 4. EXTRAER LOS COMENTARIOS DE ESTE VIDEO
    listaComentarios = obtenerComentarios(video_id)
    comentarios = []
    sentimientoAcumulado = 0
    for comentario in listaComentarios['items']:
        comment = comentario['snippet']['topLevelComment']
        texto = comment['snippet']['textDisplay']
        texto = re.sub('[^\w\s#@/:%.,_-]', '', texto, flags=re.UNICODE)
        sentimiento = analisisSentimiento(texto)
        sentimientoAcumulado+=sentimiento
        if sentimiento < 0:
            receta.c_negativo+=1
        elif sentimiento > 0:
            receta.c_positivo+=1
        else:
            receta.c_neutro+=1
        comentarios.append(texto)
    receta.comentarios = len(comentarios)
    receta.sentimiento = sentimientoAcumulado/receta.comentarios

    obtener_nutriscore(receta.texto)

    # 5. AÑADIMOS MÁS ATRIBUTOS
    receta.categoria = ''
    receta.nutriscore = ''

    print(receta.toString())

    # 6. INSERTAMOS EN LA BASE DE DATOS
    #bd.insertarReceta(receta)    