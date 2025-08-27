import httpx
import time
import random
from itertools import chain
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
from db.db_properties import update_inmueble
import re


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US;en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
}

COOKIES = {
    "SESSION": "e87100649bd6e940~e92b4b97-13c4-4461-ad9a-a2782f31986a",
    "userUUID": "47dd32a4-8b54-4223-8dc6-ff6170eb44d4",
    "datadome":"N637IcVjb2VCjR~1frjcEo1dKrIRBSqkjH25vX0Ny5lHctcWdQ1J_hs6E~UH4rEL1xMNlUs0UNBmuZLwCeWDz44d5056b0YRNrO1CeowHx7ylZeKeaKlAyQhA0Vnd6wV"
}

def actualizar_pisos():
    ids = [
    "107761619"
    ]



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

    for id in ids:
        time.sleep(random.randint(4, 8))
        try:
            with httpx.Client(headers=HEADERS, cookies=COOKIES, follow_redirects=True) as session:
                response = session.get(f"https://www.idealista.com/inmueble/{id}/")

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    titulo = soup.find('span', {'class': 'main-info__title-main'}).text
                    print(titulo)
                    fecha = soup.find('div', {'class': 'ide-box-detail overlay-box mb-jumbo'}).find('p').text
                    fecha_str = " ".join(fecha.split()[-3:])
                    print(fecha_str)
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
                    print(zona, precio, resultado)
                    

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
                        "zona": zona
                    }

                    update_inmueble(datos_inmueble, datos_inmueble["link"])
                    print(f"Piso {id} actualizado", flush=True)
                else:
                    print(f"Can't scrape property: {response.url}", flush=True)
        except Exception as e:
            print(e)