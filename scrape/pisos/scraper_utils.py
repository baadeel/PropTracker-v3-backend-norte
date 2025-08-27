import httpx
import time
import random
from itertools import chain
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime, date
import unicodedata



BASE_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US;en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
}

lista_negra_inmobiliarias = ["inmobiliaria"]
lista_negra_no_inmobiliarias = ["abstenerse", "inmobiliaria", "agencias", "intermediarios"]

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto



def sacar_ids_pagina_a_pagina_parte_1(max_pagina, pagina_inicio=1):
    print("Obteniendo los ids de los inmuebles...", flush=True)
    """Scrapea los IDs de inmuebles desde múltiples páginas."""
    ids_pag = []
    for x in range(pagina_inicio, pagina_inicio + max_pagina):
        try:
            with httpx.Client(headers=BASE_HEADERS, follow_redirects=True) as session:
                response = session.get(
                    f"https://www.pisos.com/busqueda/0.1000.F002.M00000000038004-M00000000038010-M00000000038011-M00000000038032-M00000000038041-M00000000038044-M00000000038012-M00000000038015-M00000000038020-M00000000038022-M00000000038018-M00000000038025-M00000000038026.0.30X2.0.0.0X0.0.0X0X0.{x}.0.0X0.0X0.0.0/")
                if response.status_code == 200:
                    print("PISOS.COM", flush=True)
                    print(f"Página {x}", flush=True)
                    ids_pag.append(sacar_id_link_pag(response, x))
                else:
                    print(f"Can't scrape property: {response.url}", flush=True)
        except Exception as e:
            print(e)

    lista_plana = list(chain(*ids_pag))
    print("Se han obtenido " + str(len(lista_plana)) + " inmuebles", flush=True)
    return lista_plana 

def sacar_ids_pagina_a_pagina_parte_2(max_pagina, pagina_inicio=1):
    print("Obteniendo los ids de los inmuebles...", flush=True)
    """Scrapea los IDs de inmuebles desde múltiples páginas."""
    ids_pag = []
    for x in range(pagina_inicio, pagina_inicio + max_pagina):
        try:
            with httpx.Client(headers=BASE_HEADERS, follow_redirects=True) as session:
                response = session.get(
                    f"https://www.pisos.com/busqueda/0.1000.F002.M00000000038051-M00000000038031-M00000000038042-M00000000038028-M00000000038023-M00000000038034-M00000000038038-M00000000038039-M00000000038043-M00000000038046.0.30X2.0.0.0X0.0.0X0X0.{x}.0.0X0.0X0.0.0/")
                if response.status_code == 200:
                    print("PISOS.COM", flush=True)
                    print(f"Página {x}", flush=True)
                    ids_pag.append(sacar_id_link_pag(response, x))
                else:
                    print(f"Can't scrape property: {response.url}", flush=True)
        except Exception as e:
            print(e)

    lista_plana = list(chain(*ids_pag))
    print("Se han obtenido " + str(len(lista_plana)) + " inmuebles", flush=True)
    return lista_plana 


def scrapear_inmuebles_parte_1(lista_ids_links, primeros_5_inmuebles_db, inmuebles_5_nuevos):
    print("Escaneando inmuebles...", flush=True)
    """Scrapea detalles de cada inmueble y filtra los particulares."""

    cont = 1
    ids_particulares = []
    primeros_5_inmuebles = []

    if not inmuebles_5_nuevos:
        inmuebles_5_nuevos = []

    no_hay_inmuebles_nuevos = False

    for inmueble in lista_ids_links:
        if cont > 5:
            inmuebles_5_nuevos = [
                {**item, "fecha": convertir_fecha(item["fecha"]), "localizacion": "tenerife-norte-1"} for item in inmuebles_5_nuevos
            ]
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
            with httpx.Client(headers=BASE_HEADERS, follow_redirects=True) as session:
                response = session.get(link)
                soup = BeautifulSoup(response.content, 'html.parser')

                if response.status_code == 200:
                    details_blocks = soup.find_all(
                        'div', {'class': 'details__block'})

                    for block in details_blocks:
                        h1 = block.find('h1')
                        if h1:
                            titulo = h1.get_text(strip=True)

                    fecha_actualizacion = soup.find(
                        'p', {'class': 'last-update__date'}).text
                    fecha_match = re.search(
                        r"(\d{2}/\d{2}/\d{4})", fecha_actualizacion)

                    if fecha_match:
                        fecha_str = fecha_match.group(1)
                        fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
                        fecha = fecha_obj.strftime("%Y/%m/%d") 
                        
                    html_caracteristicas = soup.find('ul', {'class':'features-summary'})
                    
                    items = [li.get_text(strip=True) for li in html_caracteristicas.find_all('li')]
                    
                    def extraer_numero(texto):
                        match = re.search(r'\d+', texto)
                        return int(match.group()) if match else None

                    habs = extraer_numero(next((item for item in items if 'hab' in item), ''))
                    baños = extraer_numero(next((item for item in items if 'baño' in item), ''))
                    metros = extraer_numero(next((item for item in items if 'm²' in item and '/' not in item), ''))

                    precio_completo = soup.find('div', {'class': 'price__value'}).text
                    precio = re.sub(r'[^\d.]', '', precio_completo)    

                    zona_html = soup.find('div', {'class': 'u-wrapper breadcrumb__list'}).find_all('div')
                    zona = zona_html[-2].find('a').get_text(strip=True)

                    datos_inmueble = {}
                    datos_inmueble["id"] = id
                    datos_inmueble["link"] = link
                    datos_inmueble["titulo"] = titulo
                    datos_inmueble["fecha"] = fecha
                    datos_inmueble["plataforma"] = "pisos.com"
                    datos_inmueble["localizacion"] = "tenerife-norte"
                    datos_inmueble["metros"] = metros
                    datos_inmueble["baños"] = baños
                    datos_inmueble["habitaciones"] = habs
                    datos_inmueble["precio"] = precio
                    datos_inmueble["zona"] = zona

                    # Crear una copia'
                    datos_sin_link_titulo = {k: v for k, v in datos_inmueble.items() if k not in ["link", "titulo","metros","baños","habitaciones","precio","zona"]}
                    
                    #Borrar primer elemento y meter el nuevo inmueble
                    if len(inmuebles_5_nuevos) == 5:
                        inmuebles_5_nuevos.pop(0)

                    inmuebles_5_nuevos.append(datos_sin_link_titulo)
                    
                    if len(primeros_5_inmuebles) < 5:
                        primeros_5_inmuebles.append(datos_sin_link_titulo)

                    if es_particular(response, soup):
                        ids_particulares.append(datos_inmueble)
        except Exception as e:
            print(e)

    print("Particulares de esta página: ", ids_particulares, flush=True)
    print("Finalizado", flush=True)

    primeros_5_inmuebles = [{**item, "fecha": convertir_fecha(item["fecha"])} for item in primeros_5_inmuebles]
    return ids_particulares, primeros_5_inmuebles, no_hay_inmuebles_nuevos, inmuebles_5_nuevos

def scrapear_inmuebles_parte_2(lista_ids_links, primeros_5_inmuebles_db, inmuebles_5_nuevos):
    print("Escaneando inmuebles...", flush=True)
    """Scrapea detalles de cada inmueble y filtra los particulares."""

    cont = 1
    ids_particulares = []
    primeros_5_inmuebles = []

    if not inmuebles_5_nuevos:
        inmuebles_5_nuevos = []

    no_hay_inmuebles_nuevos = False

    for inmueble in lista_ids_links:
        if cont > 5:
            
            inmuebles_5_nuevos = [
                {**item, "fecha": convertir_fecha(item["fecha"]), "localizacion": "tenerife-norte-2"} for item in inmuebles_5_nuevos
                ]
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
            with httpx.Client(headers=BASE_HEADERS, follow_redirects=True) as session:
                response = session.get(link)
                soup = BeautifulSoup(response.content, 'html.parser')

                if response.status_code == 200:
                    details_blocks = soup.find_all(
                        'div', {'class': 'details__block'})

                    for block in details_blocks:
                        h1 = block.find('h1')
                        if h1:
                            titulo = h1.get_text(strip=True)

                    fecha_actualizacion = soup.find(
                        'p', {'class': 'last-update__date'}).text
                    fecha_match = re.search(
                        r"(\d{2}/\d{2}/\d{4})", fecha_actualizacion)

                    if fecha_match:
                        fecha_str = fecha_match.group(1)
                        fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
                        fecha = fecha_obj.strftime("%Y/%m/%d") 
                        
                    html_caracteristicas = soup.find('ul', {'class':'features-summary'})
                    
                    items = [li.get_text(strip=True) for li in html_caracteristicas.find_all('li')]
                    
                    def extraer_numero(texto):
                        match = re.search(r'\d+', texto)
                        return int(match.group()) if match else None

                    habs = extraer_numero(next((item for item in items if 'hab' in item), ''))
                    baños = extraer_numero(next((item for item in items if 'baño' in item), ''))
                    metros = extraer_numero(next((item for item in items if 'm²' in item and '/' not in item), ''))

                    precio_completo = soup.find('div', {'class': 'price__value'}).text
                    precio = re.sub(r'[^\d.]', '', precio_completo)    

                    zona_html = soup.find('div', {'class': 'u-wrapper breadcrumb__list'}).find_all('div')
                    zona = zona_html[-2].find('a').get_text(strip=True)

                    datos_inmueble = {}
                    datos_inmueble["id"] = id
                    datos_inmueble["link"] = link
                    datos_inmueble["titulo"] = titulo
                    datos_inmueble["fecha"] = fecha
                    datos_inmueble["plataforma"] = "pisos.com"
                    datos_inmueble["localizacion"] = "tenerife-norte"
                    datos_inmueble["metros"] = metros
                    datos_inmueble["baños"] = baños
                    datos_inmueble["habitaciones"] = habs
                    datos_inmueble["precio"] = precio
                    datos_inmueble["zona"] = zona

                    # Crear una copia'
                    datos_sin_link_titulo = {k: v for k, v in datos_inmueble.items() if k not in ["link", "titulo","metros","baños","habitaciones","precio","zona"]}
                    
                    #Borrar primer elemento y meter el nuevo inmueble
                    if len(inmuebles_5_nuevos) == 5:
                        inmuebles_5_nuevos.pop(0)

                    inmuebles_5_nuevos.append(datos_sin_link_titulo)
                    
                    if len(primeros_5_inmuebles) < 5:
                        primeros_5_inmuebles.append(datos_sin_link_titulo)

                    if es_particular(response, soup):
                        ids_particulares.append(datos_inmueble)
        except Exception as e:
            print(e)

    print("Particulares de esta página: ", ids_particulares, flush=True)
    print("Finalizado", flush=True)

    primeros_5_inmuebles = [{**item, "fecha": convertir_fecha(item["fecha"])} for item in primeros_5_inmuebles]
    return ids_particulares, primeros_5_inmuebles, no_hay_inmuebles_nuevos, inmuebles_5_nuevos


def sacar_id_link_pag(response, pagina_actual_link):
    """Extrae los IDs de los inmuebles en una página dada."""
    ids = []
    soup = BeautifulSoup(response.content, 'html.parser')

    inmuebles = soup.find_all('div', {'class': 'ad-preview'})

    base_url = "https://www.pisos.com"

    # Extraer id y link
    ids_links = [
        {"id": div['id'], "link": base_url + div['data-lnk-href']}
        for div in inmuebles 
        if div.has_attr('data-lnk-href') and div.has_attr('id')
    ]
    
    return ids_links



def es_particular(response, soup):
    """Verifica si el inmueble es de un particular."""
    soup = BeautifulSoup(response.content, 'html.parser')
    owner_info = soup.find('div', {'class': 'owner-info'})
    if owner_info.find('p', {'class': 'owner-info__reference'}):
        return False
    
    nombre_tag = owner_info.find('p', {'class': 'owner-info__name'})
    if not nombre_tag:
        print("No nombre", flush=True)
        return True
    
    particular_nombre = nombre_tag.text.strip()
    nombre_normalizado = normalizar(particular_nombre)

    # Comprobar que no contenga palabras de la lista negra
    for palabra in lista_negra_inmobiliarias:
        if palabra in nombre_normalizado:
            return False
    
    return True

def convertir_fecha(fecha_str):
    if isinstance(fecha_str, date):
        return fecha_str

    try:
        return datetime.strptime(fecha_str, "%Y/%m/%d").date()
    except (ValueError, TypeError):
        print(f"Error al convertir fecha: {fecha_str}")
        return None