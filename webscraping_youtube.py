import pprint
from pytube import YouTube
import re
import requests

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from apiclient.discovery import build


def get_youtube():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    #api_service_name = "youtube"
    #api_version = "v3"
    #client_secrets_file = "client.apps.googleusercontent.com.json"

    # Get credentials and create an API client
    '''flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    
    return youtube'''
    # Arguments that need to passed to the build function
    DEVELOPER_KEY = "AIzaSyDjUEDI167EKbkAV9VocPKsG3ZPZyruhro"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey = DEVELOPER_KEY)
    return youtube_object
    
    
def get_video_json(video_id):
    youtube=get_youtube()
    request = youtube.videos().list(
        part='snippet',
        id=video_id,
    )
    response = request.execute()
    
    video_json=[]
    
    for item in response['items']:
        video_id = item['id']
        video_title = item['snippet']['title']
        descripcion = item['snippet']['description']
        fecha_publicado = item['snippet']['publishedAt']
        canal_id = item['snippet']['channelId']
        canal_name=item['snippet']['channelTitle']
        
        video_json.append({
            'video_id': video_id,
            'video_titulo':video_title,
            'fecha_publicado':fecha_publicado,
            'canal_id': canal_id,
            'canal_nombre':canal_name
        })
    
    return video_json
    
def get_canal_id(video_id):
    youtube=get_youtube()

    video_json=get_video_json(video_id)
    
    result_id=[]

    result_id.append({
        'video_id': video_json[0]['video_id'],
        'channel_id': video_json[0]['canal_id']
    })
        
    print(result_id)
    

def buscar_comentarios(video_id, video_json):
    youtube=get_youtube()
    
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=50
    )

    response = request.execute()
    
    result_comment = []
    for item in response['items']:
        commentario = item['snippet']['topLevelComment']
        autor = commentario['snippet']['authorDisplayName']
        texto = commentario['snippet']['textDisplay']
        result_comment.append(
            {
                'video_id': video_json['video_id'],
                'titulo_video': video_json['video_titulo'],
                'autor': autor,
                'comentario': texto
            }
        )
    return result_comment

def get_id_video(url):
    yt = YouTube(url)
    video_id = yt.video_id
    return video_id

def guardar_comentarios(json_comentarios):
    comentarios_array=[]
    
    for comment in json_comentarios:
        comm = re.sub('[^\w\s#@/:%.,_-]', '', comment['comentario'], flags=re.UNICODE)
        comentarios_array.append(comm)
        
    return comentarios_array

if __name__ == '__main__':

    video_id=get_id_video('https://www.youtube.com/watch?v=wkBUMvS-2ik')
    print(video_id)

    video_json=get_video_json(video_id)

    pp = pprint.PrettyPrinter(indent=4)
    comentarios = buscar_comentarios(video_json[0]['video_id'],video_json[0])

    print(len(comentarios))
    
    array_comentarios=guardar_comentarios(comentarios)
    for i in array_comentarios:
        print(i)
        print('--------------------')