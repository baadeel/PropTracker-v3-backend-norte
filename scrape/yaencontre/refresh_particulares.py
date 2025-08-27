from db.db_properties import get_properties_yaencontre, add_propertie, borrar_inmuebles_todos, guardar_en_inmuebles_todos, obtener_inmuebles_todos
from .scraper_utils import sacar_ids_pagina_a_pagina, scrapear_inmuebles, convertir_fecha
import time


def refresh_particulares():
    print("dentro", flush=True)
    particulares_old_dict = old_properties_to_dict()
    nuevos_inmuebles = []
    primeros_5_inmuebles_totales = []
    inmuebles_5_nuevos = []


    try:
        lista_realdictrow = obtener_inmuebles_todos("yaencontre", "tenerife-norte")
        primeros_5_inmuebles_db = [dict(row) for row in lista_realdictrow]
    except:
        print("Error al obtener los primeros 5 inmuebles de la DB", flush=True)

    contador_pag = 1
    contador_iguales = 0

    while True:

        ids_pag = sacar_ids_pagina_a_pagina(contador_pag)
        time.sleep(5)
        ids_particulares, primeros_5, no_hay_inmuebles_nuevos, inmuebles_5_nuevos = scrapear_inmuebles(ids_pag, primeros_5_inmuebles_db, inmuebles_5_nuevos)

        if contador_pag == 1:
            primeros_5_inmuebles_totales = primeros_5

        for inmueble in ids_particulares:
            inmueble_id = inmueble["id"]

            if inmueble_id in particulares_old_dict:
                print(
                    f"El inmueble con ID {inmueble_id} ya existe: {particulares_old_dict[inmueble_id]}", flush=True)
                datos_inmueble_old = particulares_old_dict[inmueble_id]
                fecha_old = datos_inmueble_old["fecha"]
                fecha_new = inmueble["fecha"]

                if (fecha_old == fecha_new):
                    contador_iguales += 1
                    print("Mismo id y misma fecha", flush=True)
            else:
                print(
                    f"El inmueble con ID {inmueble_id} no existe en el diccionario.", flush=True)

                add_propertie(inmueble)
                nuevos_inmuebles.append(inmueble) 
           
        if (contador_pag == 9):
            print("Máximo de páginas alcanzado", flush=True)
            break

        if (contador_iguales >= 3):
            print("Hay muchos repetidos", flush=True)
            break
            
        if(primeros_5_inmuebles_totales == primeros_5_inmuebles_db):
            print("Los 5 primeros son iguales a los 5 de la DB", flush=True)
            break

        # Guardar los 5 primeros inmuebles analizados de la primera página
        if primeros_5_inmuebles_totales and contador_pag == 1:
            print("Guardando los 5 primeros inmuebles de análisis en inmuebles_todos", flush=True)
            borrar_inmuebles_todos("yaencontre", "tenerife-norte")
            for inmueble in primeros_5_inmuebles_totales:
                guardar_en_inmuebles_todos(inmueble)
        else:
            print("No se encontraron inmuebles para guardar en inmuebles_todos", flush=True)

        if no_hay_inmuebles_nuevos:
            print("No hay inmuebles nuevos", flush=True)
            break

        contador_pag += 1


def old_properties_to_dict():
    particulares_old = get_properties_yaencontre()
    particulares_old_ids_dict = {}

    for inmueble in particulares_old:
        inmueble_id = inmueble["id_portal"]
        # Guardamos el inmueble por su id
        particulares_old_ids_dict[inmueble_id] = inmueble

    return particulares_old_ids_dict
