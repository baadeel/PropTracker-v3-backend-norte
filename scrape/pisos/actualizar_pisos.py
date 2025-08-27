import httpx
import time
import random
from itertools import chain
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
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
    links = [
    "https://www.pisos.com/comprar/piso-guia_de_isora_centro_urbano-54240937892_109800/",
    "https://www.pisos.com/comprar/piso-barrio_tagoro-54263731603_109800/",
    "https://www.pisos.com/comprar/piso-costa_del_silencio_las_galletas38631-54169122819_109800/",
    "https://www.pisos.com/comprar/piso-san_cristobal_de_la_laguna_capital38201-54205984442_109800/",
    "https://www.pisos.com/comprar/chalet_adosado-arona_chayofa38652-54253020379_109800/",
    "https://www.pisos.com/comprar/piso-ifara_residencial_anaga38001-52554264810_109800/",
    "https://www.pisos.com/comprar/piso-los_gladiolos_chapatal38007-54193140534_109800/",
    "https://www.pisos.com/comprar/casa_adosada-adeje_costa_adeje38679-54202532875_109800/",
    "https://www.pisos.com/comprar/piso-guargacho_guaza_cho38632-54192689601_109800/",
    "https://www.pisos.com/comprar/casa_adosada-barrio_tagoro-54192709185_109800/",
    "https://www.pisos.com/comprar/piso-el_escobonal-54264587284_109800/",
    "https://www.pisos.com/comprar/estudio-el_escobonal-54186782224_109800/",
    "https://www.pisos.com/comprar/apartamento-granadilla_de_abona_el_medano38612-54245169032_109800/",
    "https://www.pisos.com/comprar/piso-la_cuesta_finca_espana_los_valles38320-54216583280_109800/",
    "https://www.pisos.com/comprar/casa_unifamiliar-granadilla_de_abona_charco_del_pino38595-54258599851_109800/",
    "https://www.pisos.com/comprar/piso-la_cuesta_finca_espana_los_valles38320-54256158926_109800/",
    "https://www.pisos.com/comprar/duplex-granadilla_de_abona_san_isidro38611-54254808474_109800/",
    "https://www.pisos.com/comprar/apartamento-el_botanico38400-54194282529_109800/",
    "https://www.pisos.com/comprar/casa_adosada-villa_de_adeje38670-54255689208_109800/",
    "https://www.pisos.com/comprar/casa_adosada-san_cristobal_de_la_laguna_capital38201-54208183678_109800/",
    "https://www.pisos.com/comprar/chalet_unifamiliar-san_antonio_las_arenas38400-54170969733_109800/",
    "https://www.pisos.com/comprar/estudio-playa_jardin-54250116166_109800/",
    "https://www.pisos.com/comprar/piso-centro_ifara_toscal38001-54236120315_109800/",
    "https://www.pisos.com/comprar/chalet_unifamiliar-andaga-54190455530_109800/",
    "https://www.pisos.com/comprar/casa_rustica-guia_de_isora_centro_urbano-54208425087_109800/",
    "https://www.pisos.com/comprar/piso-centro_ifara_toscal38001-54167985053_109800/",
    "https://www.pisos.com/comprar/piso-playa_de_la_arena-54245859581_109800/",
    "https://www.pisos.com/comprar/piso-costa_del_silencio_las_galletas38630-54216589174_109800/",
    "https://www.pisos.com/comprar/piso-la_guancha-54222582080_109800/",
    "https://www.pisos.com/comprar/duplex-granadilla_de_abona_san_isidro38611-54225009700_109800/",
    "https://www.pisos.com/comprar/chalet_unifamiliar-alvaro_farina-54229929854_109800/",
    "https://www.pisos.com/comprar/loft-arona_playa_de_las_americas38650-54196748644_109800/",
    "https://www.pisos.com/comprar/casa_adosada-villa_de_adeje38670-54237175876_109800/",
    "https://www.pisos.com/comprar/apartamento-candelaria_playa_de_la_viuda-54247894616_109800/",
    "https://www.pisos.com/comprar/piso-salamanca_uruguay_las_mimosas38006-55023929746_109800/",
    "https://www.pisos.com/comprar/piso-taco_geneto_las_chumberas_guajara_los_andenes38108-55013121151_109800/",
    "https://www.pisos.com/comprar/piso-zona_martianez-55070709340_109800/",
    "https://www.pisos.com/comprar/piso-san_cristobal_de_la_laguna_capital38203-55060109701_109800/",
    "https://www.pisos.com/comprar/casa_adosada-arona_chayofa38652-51669302856_109800/",
    "https://www.pisos.com/comprar/piso-arona_el_fraile38632-55074959049_109800/",
    "https://www.pisos.com/comprar/casa_unifamiliar-la_salle_el_cabo_los_llanos38003-55039109781_109800/",
    "https://www.pisos.com/comprar/piso-playa_de_la_arena-44206692409_109800/",
    "https://www.pisos.com/comprar/piso-zona_martianez-55006507033_109800/",
    "https://www.pisos.com/comprar/duplex-icod_de_los_vinos_centro_urbano-55085166698_109800/",
    "https://www.pisos.com/comprar/piso-costa_del_silencio_las_galletas38630-55044189574_109800/",
    "https://www.pisos.com/comprar/piso-arona_el_fraile38632-55025976164_109800/",
    "https://www.pisos.com/comprar/piso-la_salle_el_cabo_los_llanos38003-55028679824_109800/",
    "https://www.pisos.com/comprar/piso-san_cristobal_de_la_laguna_capital38205-55091952660_109800/",
    "https://www.pisos.com/comprar/chalet_adosado-barranco_hondo_distrito38510-55020883034_109800/",
    "https://www.pisos.com/comprar/casa_adosada-camino_de_la_ladera-45871148320_109800/",
    "https://www.pisos.com/comprar/casa_unifamiliar-las_cuevecitas_malpais38509-55028536409_109800/",
    "https://www.pisos.com/comprar/piso-taco_geneto_las_chumberas_guajara_los_andenes38108-55073022633_109800/"
    ]

    for link in links:
        time.sleep(random.randint(4, 8))
        try:
            with httpx.Client(headers=HEADERS, cookies=COOKIES, follow_redirects=True) as session:
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
                    
                            
                    # Extraemos los textos de los <li>
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
                    datos_inmueble["titulo"] = titulo
                    datos_inmueble["fecha"] = fecha
                    datos_inmueble["plataforma"] = "pisos.com"
                    datos_inmueble["localizacion"] = "tenerife-norte"
                    datos_inmueble["metros"] = metros
                    datos_inmueble["baños"] = baños
                    datos_inmueble["habitaciones"] = habs
                    datos_inmueble["precio"] = precio
                    datos_inmueble["zona"] = zona

                    update_inmueble(datos_inmueble, link)
                    print(f"Piso {link} actualizado", flush=True)
                else:
                    print(f"Can't scrape property: {response.url}", flush=True)
        except Exception as e:
            print(e)