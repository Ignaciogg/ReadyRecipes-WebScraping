from time import sleep
import warnings
import json

import urllib.request
import pandas as pd
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup as bs
import numpy as np

warnings.filterwarnings('ignore')

urlApi = "http://127.0.0.1:8000/api/nuevoPrecio"
urlAlimento = "http://127.0.0.1:8000/api/alimentos"
supermercado = "mercadona"

def precios():
    response = requests.get(urlAlimento)
    alimentos = response.json()
    for alimento in alimentos:
        id = alimento["id"]
        nombre = alimento["nombre"]

        ingredient = nombre.replace(' ','+')
        try:
            url_productos = requests.get('https://soysuper.com/search?q='+ ingredient +'&supermarket='+ supermercado)
            soup_productos = bs(url_productos.content, 'lxml')
            precios = soup_productos.find_all(class_="price")
            
            price = [i.text for i in precios]
            price = price[:1][0]
            price = price.split()[0]
            price = price.replace(',','.').replace('€','')
            price = float(price)

            precio = {"id_Alimento": id, "precio": price, "supermercado": supermercado}
            precio_json = json.dumps(precio).encode('utf-8')
            req = urllib.request.Request(urlApi, precio_json)
            req.add_header('Content-Type', 'application/json')
            respuesta = urllib.request.urlopen(req)
            response_text = respuesta.read().decode('utf-8')
            response_text = json.loads(response_text)
            print(response_text)
            sleep(1)
        except:
            print("Error al insertar el precio de: ", nombre)

precios()
