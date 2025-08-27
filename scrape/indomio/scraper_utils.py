import httpx
import time
import random
from itertools import chain
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
import re
import unicodedata


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US;en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
}

COOKIES = {
    "datadome":"y5~JoPGOs9vk6LSZEu8h9IyDlZ7qQ_Hm16S6x9v0LAkbC~o14PgCM0Af9AEFi2wryW7g6HTNyvZXlNHSggZrYocqZrr_4YqmKxF7G8PfoZUvsQD0WIjHu1Nv9WiGP9TL"
}

lista_negra_no_inmobiliarias = ["abstenerse", "inmobiliaria", "agencias", "intermediarios"]

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto


def scrapear_listas_de_inmuebles(pagina, primeros_5_inmuebles_db, inmuebles_5_nuevos):
    #Dado desde que la lista se puede ver si es particular o no, lo hacemos así
    print("Obteniendo los ids de los inmuebles...", flush=True)
    """Scrapea los IDs de inmuebles desde múltiples páginas."""
    ids_particulares = []
    primeros_5_inmuebles = []
    no_hay_inmuebles_nuevos = False
    if not inmuebles_5_nuevos:
        inmuebles_5_nuevos = []
   
    try:
        with httpx.Client(headers=HEADERS, cookies=COOKIES, follow_redirects=True) as session:
            response = session.get(
                f"https://www.indomio.es/api-next/search-list/listings/?vrt=28.107781,-16.455803;28.193146,-16.605835;28.233988,-16.730804;28.254735,-16.773376;28.253254,-16.846161;28.354184,-16.976898;28.454445,-16.786011;28.493074,-16.536072;28.565467,-16.416595;28.667937,-16.121887;28.557023,-16.025757;28.42184,-16.044983;28.27681,-16.23999;28.107781,-16.455803&idContratto=1&idCategoria=1&criterio=dataModifica&ordine=desc&__lang=es&pag={pagina}&paramsCount=7&path=/search-list/")
#                 f"https://www.indomio.es/api-next/search-list/listings/?vrt=28.107781%2C-16.455803%3B28.193146%2C-16.605835%3B28.233988%2C-16.730804%3B28.254735%2C-16.773376%3B28.253254%2C-16.846161%3B28.354184%2C-16.976898%3B28.454445%2C-16.786011%3B28.493074%2C-16.536072%3B28.565467%2C-16.416595%3B28.667937%2C-16.121887%3B28.557023%2C-16.025757%3B28.42184%2C-16.044983%3B28.27681%2C-16.23999%3B28.107781%2C-16.455803&idContratto=1&idCategoria=1&criterio=dataModifica&ordine=desc&__lang=es&pag={pagina}&paramsCount=7&path=%2Fsearch-list%2F")

            if response.status_code == 200:
                print("INDOMIO", flush=True)
                print(f"Página {pagina}", flush=True)
                ids_particulares, primeros_5_inmuebles, no_hay_inmuebles_nuevos, inmuebles_5_nuevos = sacar_datos_json(response.json(), primeros_5_inmuebles_db, inmuebles_5_nuevos)

    except Exception as e:
        print(e)
    print("funcion", primeros_5_inmuebles)
    return ids_particulares, primeros_5_inmuebles, no_hay_inmuebles_nuevos, inmuebles_5_nuevos
    
def sacar_datos_json(json, primeros_5_inmuebles_db, inmuebles_5_nuevos):
    """Extrae los IDs de los inmuebles en una página dada."""
    # Sacar los resultados de los pisos
    results = json.get("results", [])

    cont = 1
    ids_particulares = []
    primeros_5_inmuebles = []

    if not inmuebles_5_nuevos:
        inmuebles_5_nuevos = []
    
    no_hay_inmuebles_nuevos = False

    for item in results:
        if cont > 5:
            inmuebles_5_nuevos_convertido = [
            {
                'id': str(item['id']),
                'plataforma': item['plataforma'],
                'localizacion': item['localizacion'],
                'fecha': datetime.strptime(item['fecha'], "%Y/%m/%d").date()
            }
            for item in inmuebles_5_nuevos
            ]   

            if inmuebles_5_nuevos_convertido == primeros_5_inmuebles_db:
                print("No hay inmuebles nuevos", flush=True)
                no_hay_inmuebles_nuevos = True
                break

        cont += 1


        advertiser = item.get("realEstate", {}).get("advertiser", {})
        id = item.get("realEstate", {}).get("id")

        
        
        titulo = item.get("realEstate", {}).get("title")
        link = item.get("seo",{}).get("url")
        datos = item.get("realEstate",{}).get("properties",{})
        habs_completo = datos[0].get("rooms")
        baños_completo = datos[0].get("bathrooms")
        metros_completo = datos[0].get("surface")
        habs = int(re.search(r'\d+', habs_completo).group()) if habs_completo else None
        baños = int(re.search(r'\d+', baños_completo).group()) if baños_completo else None
        metros = float(re.search(r'\d+\.?\d*', metros_completo).group()) if metros_completo else None

        precio = datos[0].get("price", {}).get("value")
        zona = datos[0].get("location", {}).get("city")


        datos_inmueble = {}
        datos_inmueble["id"] = id 
        datos_inmueble["link"] = link
        datos_inmueble["titulo"] = titulo
        datos_inmueble["plataforma"] = "indomio"
        datos_inmueble["localizacion"] = "tenerife-norte"
        datos_inmueble["metros"] = metros
        datos_inmueble["baños"] = baños
        datos_inmueble["habitaciones"] = habs
        datos_inmueble["precio"] = precio
        datos_inmueble["zona"] = zona
        datos_inmueble["fecha"] = date.today().strftime("%Y/%m/%d")

        datos_sin_link_titulo = {k: v for k, v in datos_inmueble.items() if k not in ["link", "titulo","metros","baños","habitaciones","precio","zona"]}

        #Borrar primer elemento y meter el nuevo inmueble
        if len(inmuebles_5_nuevos) == 5:
            inmuebles_5_nuevos.pop(0)
        inmuebles_5_nuevos.append(datos_sin_link_titulo)
        
        if len(primeros_5_inmuebles) < 5:
            primeros_5_inmuebles.append(datos_sin_link_titulo)

        if "agency" not in advertiser:
            print("Particular encontrado")
            time.sleep(random.randint(4, 8))
            with httpx.Client(headers=HEADERS, cookies=COOKIES, follow_redirects=True) as session:
                response = session.get(link)
                
                soup = BeautifulSoup(response.content, "html.parser")
                fecha_completa = soup.find('span', {'class':'styles_ld-lastUpdate__text__KLqrs'}).text
                match = re.search(r"\d{2}/\d{2}/\d{4}", fecha_completa)
                if match:
                    fecha_actualizacion = match.group()
                    fecha_obj = datetime.strptime(fecha_actualizacion, "%d/%m/%Y")
                    fecha = fecha_obj.strftime("%Y/%m/%d")
                    datos_inmueble["fecha"] = fecha
                
                quiere_inmo = quiere_inmobiliarias(response, soup)
                datos_inmueble["quiere_inmobiliaria"] = quiere_inmo
                
            ids_particulares.append(datos_inmueble)

    print("Particulares de esta página: ", ids_particulares, flush=True)
    print("Finalizado", flush=True)

    return ids_particulares, primeros_5_inmuebles, no_hay_inmuebles_nuevos, inmuebles_5_nuevos


def quiere_inmobiliarias(response, soup):
    """Verifica si el inmueble es de una inmobiliaria."""
    soup = BeautifulSoup(response.content, 'html.parser')
    
    descripcion = soup.find('div', {'class': 'styles_in-readAll__04LDT'}).find('div')

    if not descripcion:
        return True
    
    descripcion_limpia = descripcion.get_text(separator=" ")
    descripcion_normalizada = normalizar(descripcion_limpia)

    for palabra in lista_negra_no_inmobiliarias:
        palabra_normalizada = normalizar(palabra)
        if re.search(r'\b' + re.escape(palabra_normalizada) + r'\b', descripcion_normalizada):
            return False
    
    return True