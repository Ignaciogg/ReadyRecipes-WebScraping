import pandas as pd
from bs4 import BeautifulSoup as bs
import requests

from webscraping_ingredientes import buscar_ingredientes, buscador_precios_por_supermercado
from Receta import Receta


def obtener_nutriscore(texto_receta):
    food = pd.read_csv('./food.csv')
    food.drop(['Unnamed: 0'], axis=1, inplace=True)

    lista_ingredientes = buscar_ingredientes(texto_receta, food)
    data = buscador_precios_por_supermercado(lista_ingredientes, "mercadona")
    '''
    data2 = buscador_precios_por_supermercado(lista_ingredientes, "dia")
    data3 = buscador_precios_por_supermercado(lista_ingredientes, "carrefour")

    data = pd.concat([data1, data2, data3], axis=0)
    '''
    print("")
    # Añadir dos nuevas columnas al dataset
    data['Nutriscore'] = ''
    data['Valor Nutriscore'] = ''
    print(data)
    print("")

    # A partir de una lista de ingredientes, sacar un valor Nutriscore para cada ingrediente y asociarlo con un número
    for ingrediente in data["Alimento"]:

        url = "https://es.openfoodfacts.org/cgi/search.pl?search_terms={}&search_simple=1&action=process&json=1".format(ingrediente)

        response = requests.get(url)
        nutriscore = response.json()

        if "products" in nutriscore:
            productos = nutriscore["products"]
            if productos:
                producto = productos[0]

                if "nutrition_grades" in producto:

                    nutriscore = producto["nutrition_grades"]
                    # Asociamos los valores de letras a números para facilitar la media de una receta
                    if nutriscore == "a":
                        valorNutriscore = 5
                    if nutriscore == "b":
                        valorNutriscore = 4
                    if nutriscore == "c":
                        valorNutriscore = 3
                    if nutriscore == "d":
                        valorNutriscore = 2
                    if nutriscore == "e":
                        valorNutriscore = 1
                    
                    print("El valor NutriScore del alimento '{}' es '{}', {}".format(ingrediente, nutriscore, valorNutriscore))
                    
                    # Insertamos los valores dentro de nuestro data
                    idx = data[data['Alimento'] == ingrediente].index[0]
                    data.at[idx, 'Nutriscore'] = nutriscore
                    data.at[idx, 'Valor Nutriscore'] = valorNutriscore

                else:
                    print("No se encontró información sobre el valor NutriScore del alimento '{}'".format(ingrediente))
            else:
                print("No se encontró información sobre el alimento '{}'".format(ingrediente))
        else:
            print("Ocurrió un error al procesar la búsqueda")

    print("")
    print(data)
    '''
    # Para hacer la media, primero eliminamos los valores nulos en Nutriscore
    data = data.dropna(subset=['Valor Nutriscore'])
    media = data['Valor Nutriscore'].mean()

    if media < 1:
        letraMedia = 'e'
    if media > 1 & media < 2:
        letraMedia = 'd'
    if media > 2 & media < 3:
        letraMedia = 'c'
    if media > 3 & media < 4:
        letraMedia = 'b'
    if media > 4:
        letraMedia = 'a'

    print("La media del Nutriscore de esta receta es: " + str(media) + " -> " + letraMedia)'''