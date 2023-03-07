from genericpath import exists
from importlib.resources import path
from ffmpy import FFmpeg
import YoutubeDownloader as yt
import os

def convertirAudio(nombre):
    rutaEntrada = str(yt.pathVideos) + '\\' +nombre+'.mp4'
    rutaSalida = str(yt.pathAudios) + '\\'+nombre+'.wav'

    if not os.path.exists(rutaSalida):
        ff = FFmpeg(executable='C:\\ffmpeg\\bin\\ffmpeg.exe',
        inputs ={rutaEntrada: None},
        outputs ={rutaSalida: None})
        ff.run()

        try:
            os.remove(rutaEntrada)
        except:
            print("No se puede borrar vídeo")