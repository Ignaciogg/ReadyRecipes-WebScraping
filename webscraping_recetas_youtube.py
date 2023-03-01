import requests
import json

# Introduce la url del canal de YouTube
channel_url = input("Introduce la url del canal de YouTube: ")

# Extraer el ID del canal de la URL
channel_id = channel_url.split("/")[-1]

# URL para obtener los últimos 5 videos de un canal
# API Key: AIzaSyB0Z5YoVzZPgH1EOSVFJAL5X8EBb9qbSPU
url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=5&order=date&type=video&key=AIzaSyB0Z5YoVzZPgH1EOSVFJAL5X8EBb9qbSPU"

# Realizar una solicitud GET a la URL
response = requests.get(url)

# Convertir la respuesta en un objeto JSON
json_data = json.loads(response.text)

# Recorrer los resultados y extraer la URL del video
for item in json_data["items"]:
    video_id = item["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(video_url)