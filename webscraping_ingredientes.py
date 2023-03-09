import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import numpy as np
import re


food = pd.read_csv('./food.csv')
food.drop(['Unnamed: 0'], axis=1,inplace=True)

def buscador_precios_por_supermercado(array_ingredientes,supermercado):
    
    result=[]
    
    for ingredientes in array_ingredientes:
        if len(ingredientes.split()) > 1:
            ingredient = ingredientes.replace(' ','+')
            url_productos = requests.get('https://soysuper.com/search?q='+ ingredient +'&supermarket='+ supermercado)
        else:
            url_productos = requests.get('https://soysuper.com/search?q='+ ingredientes +'&supermarket=' + supermercado)
    
        soup_productos = bs(url_productos.content, 'lxml')
        productos = soup_productos.find_all(class_="productname")
        precios = soup_productos.find_all(class_="price")
        imagenes=soup_productos.find_all(class_="img")
        

        products = [i.text for i in productos]
        price = [i.text for i in precios]
        image=[]
        
        for i in imagenes:
            for j in (i.find_all('img')):
                image.append(supermercado)
                
        
        valor = np.stack((products[:3],price[:3],image[:3]), axis=1)
        
        result.append(valor.tolist())
        
    

    lista_fin_alimentos=[]
    for i in range (len(result)):
        lista_fin_alimentos.append(result[i][:1][0])

    print(lista_fin_alimentos)
    
    result_fin=pd.DataFrame(lista_fin_alimentos)

    result_fin.columns=['Alimento', 'Precio/Peso', 'Supermercado']

    return result_fin
            


def mostrar_precio_ordenado(orden, array_ingredientes):
    result=[]

    for ingredientes in array_ingredientes:
        if len(ingredientes.split()) > 1:
            ingredient = ingredientes.replace(' ','+')
            url_productos=get_url_order(orden,ingredient)
        else:
            url_productos=get_url_order(orden,ingredientes)

        soup_productos = bs(url_productos.content, 'lxml')
        productos = soup_productos.find_all(class_="productname")
        precios = soup_productos.find_all(class_="price")
        supermercados = get_url_product(soup_productos)
        
        supermercado=[]
        
        for i in supermercados:
            supermercado.append(get_supermarket(i))

        products = [i.text for i in productos]
        price = [i.text for i in precios]
        
        valor = np.stack((products[:3],price[:3],supermercado[:3]), axis=1)
        
        result.append(valor.tolist())
    
    lista_fin_alimentos=[]
    for i in range (len(result)):
        lista_fin_alimentos.append(result[i][:1][0])
    
    result_fin=pd.DataFrame(lista_fin_alimentos)

    result_fin.columns=['Alimento', 'Precio/Peso', 'Supermercado']
        
    return result_fin

def mostrar_precio_ordenado_supermercado(orden, array_ingredientes,mercado):
    result=[]

    for ingredientes in array_ingredientes:
        if len(ingredientes.split()) > 1:
            ingredient = ingredientes.replace(' ','+')
            url_productos=get_url_order_super(orden,ingredient,mercado)
        else:
            url_productos=get_url_order_super(orden,ingredientes,mercado)

        soup_productos = bs(url_productos.content, 'lxml')
        productos = soup_productos.find_all(class_="productname")
        precios = soup_productos.find_all(class_="price")
        supermercados = get_url_product(soup_productos)
        
        supermercado=[]
        
        for i in supermercados:
            supermercado.append(get_supermarket(i))

        products = [i.text for i in productos]
        price = [i.text for i in precios]
        
        valor = np.stack((products[:3],price[:3],supermercado[:3]), axis=1)
        
        result.append(valor.tolist())
    
    lista_fin_alimentos=[]
    for i in range (len(result)):
        lista_fin_alimentos.append(result[i][:1][0])
    
    result_fin=pd.DataFrame(lista_fin_alimentos)

    result_fin.columns=['Alimento', 'Precio/Peso', 'Supermercado']
        
    return result_fin

def get_supermarket(url):
    try:
        url = requests.get(url)
        soup = bs(url.content, 'lxml')
        productos = soup.find(class_="superstable")
        superm = productos.find('i')['title']
    except:
        superm = 'Not found'
    
    return superm

def get_url_product(soup_url):
    url=[]
    
    productos = soup_url.find_all('meta',itemprop="url")
    
    for url_ in productos:
        url.append(url_['content'])
        
    url.pop(0)
    
    return url

def get_url_order_super(orden, ingredient,supermercado):
    if orden == 'barato':
        url_productos = requests.get('https://soysuper.com/search?q='+ ingredient +'&supermarket='+supermercado+'&sort=value%3Aasc')
    elif orden == 'caro':
        url_productos = requests.get('https://soysuper.com/search?q='+ ingredient+'&supermarket='+supermercado+'&sort=value%3Adesc')

    return url_productos

def get_url_order(orden, ingredient):
    if orden == 'barato':
        url_productos = requests.get('https://soysuper.com/search?q='+ ingredient +'&sort=value%3Aasc')
    elif orden == 'caro':
        url_productos = requests.get('https://soysuper.com/search?q='+ ingredient+'&sort=value%3Adesc')

    return url_productos

def buscar_ingredientes(receta, lista_alimentos_csv):
    alimentos_csv_list = lista_alimentos_csv['Nombre'].values
    receta_lower=normalize(receta)
    lista_ingredientes= []
    
    for i in alimentos_csv_list:
        if re.findall(i,receta_lower):
            lista_ingredientes.append(re.findall(i,receta_lower)[:1][0])
    
    return lista_ingredientes


def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
        
    s = s.lower()
    return s
