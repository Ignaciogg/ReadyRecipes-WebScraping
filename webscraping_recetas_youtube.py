# pip install google-api-python-client
# pip install mysql.connector
# pip install pytube
# pip install SpeechRecognition

import requests
import json
import mysql.connector
import datetime
from pytube import YouTube
import os
import speech_recognition as sr

from ffmpy import FFmpeg
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

'''
mydb = mysql.connector.connect(
  host="",
  user="",
  passwd="",
  database=""
)
'''

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

#mycursor = mydb.cursor()

# 1. EXTRAER X URLs DE UN CANAL DE YOUTUBE
channel_url = 'https://www.youtube.com/@SuperGustoso'
#SuperGustoso
# Url Canal  -> https://www.youtube.com/@SuperGustoso
# Url de un video -> https://www.youtube.com/watch?v=zfD0C3_gl7Q
yt = YouTube('https://www.youtube.com/watch?v=zfD0C3_gl7Q')
channel_id = yt.channel_id

yt_key = 'AIzaSyB0Z5YoVzZPgH1EOSVFJAL5X8EBb9qbSPU'

# Define los parámetros de la solicitud
params = {
    'part': 'snippet',
    'channelId': channel_id,  # Reemplaza con el ID del canal que deseas obtener los videos
    'maxResults': 1,
    'key': yt_key  # Reemplaza con tu clave de API
}

# Realiza la solicitud a la API de YouTube
response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)

print(response.text)
json_data = json.loads(response.text)
print(json_data)
for item in json_data["items"]:
    video_id = item["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(video_url)

    # 2. COMPROBAR SI YA TENEMOS ESTA URL
    #mycursor.execute("SELECT * FROM receta WHERE url=?", (video_url,))
    #consultaURL = mycursor.fetchone()

    #if consultaURL is not None:
    if False:
        print("El URL ya existe en la tabla Recetas")
    else:
        print("El URL no existe en la tabla de recetas")

        # 3. EXTRAER LA TRANSCRIPCION DE ESTA RECETA

        transcripcion = descargarVideo(video_url)
        print(transcripcion)
        # 4. EXTRAER EL NUMERO DE COMENTARIOS DE ESTE VIDEO
        youtubeCommentConnector = build('youtube', 'v3', developerKey=yt_key)
        try:
            response = youtubeCommentConnector.commentThreads().list(
                part='snippet',
                videoId=video_id
            ).execute()

            num_comentarios = response['pageInfo']['totalResults']

        except HttpError as error:
            print(f'Ha ocurrido un error: {error}')


        # 5. AÑADIMOS MÁS ATRIBUTOS
        yt = YouTube(video_url)
        titulo = yt.title
        autor = yt.author

        fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d')
'''

        # 6. INSERTAMOS EN LA BASE DE DATOS
        sql = "INSERT INTO Receta (url, titulo, texto, categoria, comentarios, nutriscore, sentimiento, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        val = (video_url, titulo, 'Aperitivo', num_comentarios, nutriscore, 1.5, fecha_actual)
        mycursor.execute(sql, val)

        mydb.commit()


'''
        