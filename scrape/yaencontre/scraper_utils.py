import cloudscraper
import time
import random
from itertools import chain
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
import re
from datetime import datetime
import unicodedata
from scrape.listas_negras import diccionario_abstenerse


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US;en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
}

COOKIES = {
    'datadome':'PvY9~iaY083p86Dvn1~p_L7C9RYgTh9_nU4U8dDtJbKU_jvjFN~uLfqKdJTsiOcd7ur_FJKx9K6A5hInc4q7fTu4AJ66WQJQsM4dSAbtvAUArobviSzEWpoU7Qf9iN8V'
}


def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def sacar_id_link_pag(response, pagina_actual_link):
    """Extrae los IDs de los inmuebles en una página dada."""
    ids = []
    soup = BeautifulSoup(response.content, 'html.parser')
     
    inmuebles = soup.find('section', {'class': 'ThinPropertiesList'}).find_all('article')

    base_url = "https://www.yaencontre.com"

    ids_links = []

    for article in inmuebles:
        try:
            link_tag = article.find('div', { 'class':'content'}).find('h3').find('a')
            if link_tag and link_tag.has_attr('href'):
                link = base_url + link_tag['href']
                match = re.search(r'inmueble-([\w\-]+)', link)
                if match:
                    id = match.group(1)
                    ids_links.append({"id": id, "link": link})

        except Exception as e:
            print(f"Error procesando article: {e}")

    return ids_links

def sacar_ids_pagina_a_pagina(pagina=1):
    print("Obteniendo los ids de los inmuebles...", flush=True)
    """Scrapea los IDs de inmuebles desde múltiples páginas."""
    ids_pag = []

    try:
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        response = scraper.get(f'https://www.yaencontre.com/venta/pisos/custom/pag-{pagina}/o-recientes?polygon=itxkD%7Cs%60gB%7DjZuqGk%7CQobnBsjJadCepLyml%40%60dSqx%5B%3FpGbv%5Cly%60%40qFePvfVtnN%7ChCbAby%5Czh%5DxSsObxBzyB%7B%7CBxkC%7B%7ECfiHuL%7C%7BHwzA%60lF%7DvCnlAi%60H%60mQitChbEu%5DhyEdsBz%7BJ%7CmDfoM%7DuPncW', headers=HEADERS, cookies=COOKIES)

        if response.status_code == 200:
            print("YAENCONTRE", flush=True)
            print(f"Página {pagina}", flush=True)
            ids_pag.append(sacar_id_link_pag(response, pagina))
        else:
            print(f"Can't scrape property: {response.url}", flush=True)
            
    except Exception as e:
        print(e)

    lista_plana = list(chain(*ids_pag))
    print("Se han obtenido " + str(len(lista_plana)) + " inmuebles", flush=True)
    return lista_plana


# https://www.yaencontre.com/venta/piso/inmueble-u728389_53749599 particula
# https://www.yaencontre.com/venta/piso/inmueble-u14249050_53947644

# https://www.yaencontre.com/venta/piso/inmueble-u728389_53749599 particula
# https://www.yaencontre.com/venta/piso/inmueble-u14249050_53947644

def es_particular(response):
    """Verifica si el inmueble es de un particular."""
    soup = BeautifulSoup(response.content, 'html.parser')
    ref_div = soup.find('div', {'class': 'ref'})

    if ref_div:
        referencia = ref_div.text
        
        # Buscar coincidencias con el patrón que empieza por 'u'
        coincidencias = re.findall(r'u\d+(?:[_-]\d+)?', referencia)

        if coincidencias:
            # Si hay referencias que comienzan con 'u', puedes hacer lo que necesites
            return True
        else:
            return False
    else:
        print("No se encontró el div con clase 'ref'")
        return False


def convertir_fecha(fecha_str):
    if isinstance(fecha_str, date):
        return fecha_str

    try:
        return datetime.strptime(fecha_str, "%Y/%m/%d").date()
    except (ValueError, TypeError):
        print(f"Error al convertir fecha: {fecha_str}")
        return None

def scrapear_inmuebles(lista_ids_links, primeros_5_inmuebles_db, inmuebles_5_nuevos):
    print("Escaneando inmuebles...", flush=True)
    """Scrapea detalles de cada inmueble y filtra los particulares."""
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

    cont = 1
    ids_particulares = []
    primeros_5_inmuebles = []

    if not inmuebles_5_nuevos:
        inmuebles_5_nuevos = []

    no_hay_inmuebles_nuevos = False

    for inmueble in lista_ids_links:
        if cont > 5:
            inmuebles_5_nuevos = [{**item, "fecha": convertir_fecha(item["fecha"])} for item in inmuebles_5_nuevos]
            if inmuebles_5_nuevos == primeros_5_inmuebles_db:
                print("No hay inmuebles nuevos", flush=True)
                no_hay_inmuebles_nuevos = True
                break
            
        print(str(cont) + "/" + str(len(lista_ids_links)), flush=True)
                
        cont += 1
        time.sleep(random.randint(4, 8))
        id = inmueble["id"]
        link = inmueble["link"]
        try:
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
            response = scraper.get(link, headers=HEADERS, cookies=COOKIES)
            soup = BeautifulSoup(response.content, 'html.parser')
            if response.status_code == 200:
                titulo = soup.find(
                    'h1', {'class': 'details-title'}).text
                print(titulo, flush=True)

                fecha_actualizacion = soup.find('div', { 'class': 'owner-info'}).find('p', {'class': 'small-text mb-md'}).text

                if fecha_actualizacion:
                     fecha_obj = datetime.strptime(fecha_actualizacion, "%d/%m/%Y")
                     fecha = fecha_obj.strftime("%Y/%m/%d")
                
                def extraer_numero(texto):
                    match = re.search(r'\d+', texto)
                    return int(match.group()) if match else None

                def extraer_texto_seguro(soup, clase_icono):
                    contenedor = soup.find('div', {'class': clase_icono})
                    if contenedor:
                        span = contenedor.find('span')
                        if span:
                            return span.text.strip()
                    return "0"

                habs = extraer_texto_seguro(soup, 'icon-room')
                baños = extraer_texto_seguro(soup, 'icon-bath')
                metros_str = extraer_texto_seguro(soup, 'icon-meter')

                metros = extraer_numero(metros_str)

                precio_completo = soup.find('span', {'class': 'price'}).text
                precio = re.sub(r'[^\d.]', '', precio_completo)    

                zona_ul = soup.find('ul', {'class':'breadcrumb-link'})
                zona_lis = zona_ul.find_all('li')
                if len(zona_lis) >= 3:
                    zona_sucia = zona_lis[2].get_text(strip=True)
                    zona = re.sub(r'\s*\([^)]*\)', '', zona_sucia)
                else:
                    zona = None
                    print("No hay suficientes elementos <li>")

                quiere_inmo = quiere_inmobiliarias(response, soup)

                datos_inmueble = {}
                datos_inmueble["id"] = id
                datos_inmueble["link"] = link
                datos_inmueble["titulo"] = titulo
                datos_inmueble["fecha"] = fecha
                datos_inmueble["plataforma"] = "yaencontre"
                datos_inmueble["localizacion"] = "tenerife-norte"
                datos_inmueble["metros"] = metros
                datos_inmueble["baños"] = baños
                datos_inmueble["habitaciones"] = habs
                datos_inmueble["precio"] = precio
                datos_inmueble["zona"] = zona
                datos_inmueble["quiere_inmobiliaria"] = quiere_inmo

                # Crear una copia'
                datos_sin_link_titulo = {k: v for k, v in datos_inmueble.items() if k not in ["link", "titulo","metros","baños","habitaciones","precio","zona","quiere_inmobiliaria"]}
                
                #Borrar primer elemento y meter el nuevo inmueble
                if len(inmuebles_5_nuevos) == 5:
                    inmuebles_5_nuevos.pop(0)

                inmuebles_5_nuevos.append(datos_sin_link_titulo)
                
                if len(primeros_5_inmuebles) < 5:
                    primeros_5_inmuebles.append(datos_sin_link_titulo)

                if es_particular(response):
                    ids_particulares.append(datos_inmueble)
                    print("Es particular", flush=True)

        except Exception as e:
            print(e)

    print("Particulares de esta página: ", ids_particulares, flush=True)
    print("Finalizado", flush=True)

    primeros_5_inmuebles = [{**item, "fecha": convertir_fecha(item["fecha"])} for item in primeros_5_inmuebles]
    return ids_particulares, primeros_5_inmuebles, no_hay_inmuebles_nuevos, inmuebles_5_nuevos

def quiere_inmobiliarias(response, soup):
    """Verifica si el inmueble es de una inmobiliaria."""
    soup = BeautifulSoup(response.content, 'html.parser')
    
    descripcion = soup.find('div', {'class': 'description'})

    if not descripcion:
        return True
    
    descripcion_limpia = descripcion.get_text(separator=" ")
    descripcion_normalizada = normalizar(descripcion_limpia)

    for palabra in diccionario_abstenerse:
        palabra_normalizada = normalizar(palabra)
        if re.search(r'\b' + re.escape(palabra_normalizada) + r'\w*\b', descripcion_normalizada):
            return False

    return True