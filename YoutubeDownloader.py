#pip install pytube

from pytube import YouTube
import os
from pathlib import Path
from Receta import Receta
import SpeechRecognition as SpeechRecognition
import AudioConverter as AudioConverter

pathVideos=Path().absolute() / 'Videos'
pathAudios=Path().absolute() / 'Audios'
pathTextos=Path().absolute() / 'Textos'
listaCategorías = ["Aperitivos","Carne","Pasta","Pescado", "Verdura", "Otros"]

#Comprobar que existen los directorios
try:
    os.stat(pathVideos)
    os.stat(pathAudios)
    os.stat(pathTextos)
except:
    os.mkdir(pathVideos)
    os.mkdir(pathAudios)
    os.mkdir(pathTextos)

def descargarVideo(url):
    if comprobarNuevo(url):
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
        return False
    else:
        print('ERROR. El video está duplicado')
        return True

def comprobarNuevo(url):
    nuevo = True
    i = 0
    while nuevo and i < len(listaCategorías):
        ruta = str(pathTextos) + '\\' + listaCategorías[i]
        listaTextos = os.listdir(ruta)
        j = 0
        while nuevo and j < len(listaTextos):
            enlaceReceta = ruta + '\\' + listaTextos[j]
            with open(enlaceReceta, 'r', encoding="utf-8") as f:
                urlReceta = f.readline()[:-1]
                if url == urlReceta:
                    nuevo = False
                f.close()
            j += 1
        i += 1
    return nuevo