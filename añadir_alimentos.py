import warnings
import json

import urllib.request
import pandas as pd
import requests
from urllib.parse import quote

warnings.filterwarnings('ignore')

urlApi = "http://127.0.0.1:8000/api/nuevoAlimento"


def nutriscore():
    food = pd.read_csv('./food.csv')
    alimentos_csv_list = food['Nombre'].values
    alimentos = alimentos_csv_list.tolist()
    letras_a_numeros = {"a": 5, "b": 4, "c": 3, "d": 2, "e": 1}
    for alimento in alimentos:
        url = f"https://es.openfoodfacts.org/cgi/search.pl?search_terms={quote(alimento)}&search_simple=1&action=process&json=1"
        response = requests.get(url)
        nutriscore = response.json()
        nutriscores = []
        media = 0
        if "products" in nutriscore and nutriscore["products"]:
            for producto in nutriscore["products"]:
                if "nutrition_grades" in producto: #si el producto tiene nutriscore lo guardamos para hacer la media
                    nutriscores.append(letras_a_numeros[producto["nutrition_grades"]])
        if nutriscores:
            media = round(sum(nutriscores) / len(nutriscores), 0)
        #enviamos una peticion a la api para guardar el nutriscore
        alimento = {"nombre": alimento, "nutriscore": media}
        alimento_json = json.dumps(alimento).encode('utf-8')
        print(alimento_json)
        req = urllib.request.Request(urlApi, alimento_json)
        req.add_header('Content-Type', 'application/json')
        respuesta = urllib.request.urlopen(req)
        response_text = respuesta.read().decode('utf-8')
        print(response_text)

nutriscore()
