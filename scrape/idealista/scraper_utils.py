import httpx
import time
import random
from itertools import chain
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
import re
import unicodedata


# jejejej
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US;en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
}

COOKIES = {
    "SESSION": "e87100649bd6e940~e92b4b97-13c4-4461-ad9a-a2782f31986a",
    "userUUID": "47dd32a4-8b54-4223-8dc6-ff6170eb44d4",
    "datadome":"hayRn4pCxpb20NBec7I14irTdqeexam2TdbBGFVOnE9zyho9kVHw2ZavtlikGvpCOYH8ciNIY_OXn11JSkzA04RUaHvqBSkrZVF_A_k~ikHGBjj1b8ia0XMA90z4kg9z"
}

lista_negra_inmobiliarias = ["inmobiliaria"]
lista_negra_no_inmobiliarias = ["abstenerse", "inmobiliaria", "agencias", "intermediarios"]

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def sacar_ids_pagina_a_pagina(max_pagina, pagina_inicio=1):
    
    print("Obteniendo los ids de los inmuebles...", flush=True)
    """Scrapea los IDs de inmuebles desde múltiples páginas."""
    ids_pag = []
    for x in range(pagina_inicio, pagina_inicio + max_pagina):
        try:
            with httpx.Client(headers=HEADERS, cookies=COOKIES, follow_redirects=True) as session:
                response = session.get(
                    f"https://www.idealista.com/areas/venta-viviendas/pagina-{x}?shape=%28%28kodlDhhnfBevEgoQ%60NwmIytFkm%5Cmsa%40wkx%40uuGuov%40%60%7Bg%40u%7CMnz%5Ed%7Ct%40hxi%40bzRutFfnOcyH%7CzIyaH%7Ey%5EezHnlVtS%7CnFeaLliNokHbaF%29%29&ordenado-por=fecha-publicacion-desc")

                if response.status_code == 200:
                    print("IDEALISTA", flush=True)
                    print(f"Página {x}", flush=True)
                    ids_pag.append(sacar_id_pag(response, x))
                else:
                    print(f"Can't scrape property: {response.url}", flush=True)
        except Exception as e:
            print(e)

    lista_plana = list(chain(*ids_pag))
    print("Se han obtenido " + str(len(lista_plana)) + " inmuebles", flush=True)
    return lista_plana  # Aplanar lista

def scrapear_inmuebles(lista_ids, primeros_5_inmuebles_db, inmuebles_5_nuevos):
    print("Escaneando inmuebles...", flush=True)
    cont = 1
    ids_particulares = []
    primeros_5_inmuebles = []
    
    if not inmuebles_5_nuevos:
        inmuebles_5_nuevos = []

    no_hay_inmuebles_nuevos = False

    meses = {
        'enero': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12
    }

    for id in lista_ids:
        if cont > 5:
            if inmuebles_5_nuevos == primeros_5_inmuebles_db:
                print("No hay inmuebles nuevos", flush=True)
                no_hay_inmuebles_nuevos = True
                break
            
        print(str(cont) + "/" + str(len(lista_ids)), flush=True)
                
        cont += 1
        time.sleep(random.randint(4, 8))
        try:
            with httpx.Client(headers=HEADERS, cookies=COOKIES, follow_redirects=True) as session:
                response = session.get(f"https://www.idealista.com/inmueble/{id}/")
                soup = BeautifulSoup(response.content, 'html.parser')
                if response.status_code == 200:
                    titulo = soup.find('span', {'class': 'main-info__title-main'}).text
                    fecha = soup.find('div', {'class': 'ide-box-detail overlay-box mb-jumbo'}).find('p').text
                    fecha_str = " ".join(fecha.split()[-3:])
                    dia, _, mes_str = fecha_str.partition(" de ")
                    anio_actual = date.today().year
                    fecha = date(anio_actual, meses[mes_str.lower()], int(dia))
                    precio = soup.find('span', { 'class':'info-data-price'}).find('span').text

                    caracteristicas_h2 = soup.find('h2', string='Características básicas')
                    div_bajo_h2 = caracteristicas_h2.find_next_sibling('div')
                    caracteristicas_basicas = div_bajo_h2.find_all('li')
                    li_texts = [li.get_text(strip=True) for li in caracteristicas_basicas]
                    filtros = ['baño', 'habitaci', 'm² c']
                    filtrados = [txt for txt in li_texts if any(f in txt.lower() for f in filtros)]
                    datos = [texto.split(',')[0].strip() for texto in filtrados]

                    resultado = {}

                    for texto in datos:
                        match = re.search(r'\d+', texto)
                        if match:
                            numero = int(match.group())
                        else:
                            numero = 0  # o cualquier valor por defecto que quieras

                        texto_lower = texto.lower()
                        
                        if 'm²' in texto_lower or 'construidos' in texto_lower:
                            resultado['metros'] = numero
                        elif 'habitaci' in texto_lower:
                            resultado['habitaciones'] = numero
                        elif 'baño' in texto_lower:
                            resultado['baños'] = numero

                    zona_completa_html = soup.find('div', {'id': 'headerMap'}).find_all('li')
                    zona_html = zona_completa_html[-2] 
                    zona = zona_html.get_text(strip=True)

                    quiere_inmo = quiere_inmobiliarias(response, soup)


                    datos_inmueble = {
                        "id": id,
                        "link": f"https://www.idealista.com/inmueble/{id}/",
                        "titulo": titulo,
                        "fecha": fecha,
                        "plataforma": "idealista",
                        "localizacion": "tenerife-norte",
                        "metros": resultado.get("metros"),
                        "habitaciones": resultado.get("habitaciones"),
                        "baños": resultado.get("baños"),
                        "precio": precio,
                        "zona": zona,
                        "quiere_inmobiliaria": quiere_inmo
                    }

                    # Crear una copia
                    datos_sin_link_titulo = {k: v for k, v in datos_inmueble.items() if k not in ["link", "titulo","metros", "baños","habitaciones","precio","zona"]}
                    
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
    return ids_particulares, primeros_5_inmuebles, no_hay_inmuebles_nuevos, inmuebles_5_nuevos


def sacar_id_pag(response, pagina_actual_link):
    """Extrae los IDs de los inmuebles en una página dada."""
    ids = []
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        pagina_actual = int(soup.find('main', {'class': 'listing-items'}).find(
            'div', {'class': 'pagination'}).find('li', {'class': 'selected'}).text)
    except:
        pagina_actual = 1

    if pagina_actual != pagina_actual_link:
        print("Máximo de páginas alcanzado", flush=True)
        return []

    articles = soup.find(
        'main', {'class': 'listing-items'}).find_all('article')

    for article in articles:
        id_muebles = article.get('data-element-id')
        if id_muebles:
            ids.append(id_muebles)

    return ids


def es_particular(response, soup):
    """Verifica si el inmueble es de un particular."""
    soup = BeautifulSoup(response.content, 'html.parser')
    nombre_tag = soup.find('div', {'class': 'professional-name'})

    if nombre_tag and nombre_tag.find('span', {'class': 'particular'}):
        particular_nombre = nombre_tag.find('span', {'class': 'particular'}).text.strip()
        nombre_normalizado = normalizar(particular_nombre)
    
        # Comprobar que no contenga palabras de la lista negra
        for palabra in lista_negra_inmobiliarias:
            if palabra in nombre_normalizado:
                return False

        return True

    return False

def quiere_inmobiliarias(response, soup):
    """Verifica si el inmueble es de una inmobiliaria."""
    soup = BeautifulSoup(response.content, 'html.parser')
    
    descripcion = soup.find('div', {'class': 'adCommentsLanguage'}).find('p')

    if not descripcion:
        return True
    
    descripcion_limpia = descripcion.get_text(separator=" ")
    descripcion_normalizada = normalizar(descripcion_limpia)

    for palabra in lista_negra_no_inmobiliarias:
        palabra_normalizada = normalizar(palabra)
        if re.search(r'\b' + re.escape(palabra_normalizada) + r'\b', descripcion_normalizada):
            return False
    
    return True