# pip install google-api-python-client
# pip install mysql.connector

import AudioConverter as AudioConverter
import YoutubeDownloader as YoutubeDownloader

import requests
import json
import mysql.connector
import datetime
from pytube import YouTube
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

mydb = mysql.connector.connect(
  host="",
  user="",
  passwd="",
  database=""
)

mycursor = mydb.cursor()

# 1. EXTRAER X URLs DE UN CANAL DE YOUTUBE
channel_url = 'https://www.youtube.com/@SuperGustoso'
channel_id = channel_url.split("/")[-1]
yt_key = 'AIzaSyB0Z5YoVzZPgH1EOSVFJAL5X8EBb9qbSPU'

url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=1&order=date&type=video&key={yt_key}"

response = requests.get(url)
json_data = json.loads(response.text)

for item in json_data["items"]:
    video_id = item["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(video_url)

    # 2. COMPROBAR SI YA TENEMOS ESTA URL
    mycursor.execute("SELECT * FROM receta WHERE url=?", (video_url,))
    consultaURL = mycursor.fetchone()

    if consultaURL is not None:
        print("El URL ya existe en la tabla Recetas")
    else:
        print("El URL no existe en la tabla de recetas")

        
        # 3. EXTRAER LA TRANSCRIPCION DE ESTA RECETA
        def descargarVideo(url):
            yt = YouTube(url)
            titulo = yt.title
            autor = yt.author
            t = yt.streams.filter(only_audio=True).first()
            nombre = 'Otros'+str(len(os.listdir(str(pathTextos) + '\\' + 'Otros'))+1)
            t.download(pathVideos, nombre+'.mp4')
            AudioConverter.convertirAudio(nombre)
            try:
                texto = SpeechRecognition.transcribirAudio(nombre)
                receta = Receta(titulo, url, autor, texto).guardarTexto(str(pathTextos)+'\\'+'Otros'+'\\'+nombre+'.txt')
            except:
                print('ERROR. Audio mayor 10MB')
                os.remove(str(pathAudios) + '\\'+nombre+'.wav')


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

        # 6. INSERTAMOS EN LA BASE DE DATOS
        sql = "INSERT INTO Receta (url, titulo, texto, categoria, comentarios, nutriscore, sentimiento, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        val = (video_url, titulo, 'Aperitivo', num_comentarios, nutriscore, 1.5, fecha_actual)
        mycursor.execute(sql, val)

        mydb.commit()