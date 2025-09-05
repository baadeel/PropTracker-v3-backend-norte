import psycopg2
import psycopg2.extras

from .db_connection import get_connection


def get_properties_idealista():
    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM inmuebles WHERE plataforma = 'idealista'")
            inmuebles = cur.fetchall()

        conn.close()
        return inmuebles

    except Exception as e:
        print("Error get_properties: " + e)

def get_properties_indomio():
    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM inmuebles WHERE plataforma = 'indomio'")
            inmuebles = cur.fetchall()

        conn.close()
        return inmuebles

    except Exception as e:
        print("Error get_properties: " + e)

def get_properties_pisos_com():
    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM inmuebles WHERE plataforma = 'pisos.com'")
            inmuebles = cur.fetchall()

        conn.close()
        return inmuebles

    except Exception as e:
        print("Error get_properties: " + e)

def get_properties_yaencontre():
    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM inmuebles WHERE plataforma = 'yaencontre'")
            inmuebles = cur.fetchall()

        conn.close()
        return inmuebles

    except Exception as e:
        print("Error get_properties: " + e)



def add_propertie(inmueble):
    try:
        # Conectamos a la base de datos
        conn = get_connection()

        # Usamos el cursor para ejecutar la consulta
        with conn.cursor() as cur:
            # La sentencia SQL para insertar un nuevo inmueble
            insert_query = """
            INSERT INTO inmuebles (id_portal, titulo, fecha, localizacion, plataforma, link, precio, habitaciones, baños, metros, zona, quiere_inmobiliaria, tiene_telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Obtenemos los valores del diccionario
            inmueble_id = inmueble['id']
            link = inmueble['link']
            titulo = inmueble['titulo']
            fecha = inmueble['fecha']
            localizacion = inmueble['localizacion']
            plataforma = inmueble['plataforma']
            precio = inmueble['precio']
            habitaciones = inmueble['habitaciones']
            banos = inmueble['baños']
            metros = inmueble['metros']
            zona = inmueble['zona']
            quiere_inmobiliaria = inmueble['quiere_inmobiliaria']
            tiene_telefono = inmueble['tiene_telefono']

            # Ejecutamos la consulta con los valores extraídos del diccionario
            cur.execute(insert_query, (inmueble_id, titulo, fecha, localizacion, plataforma, link, precio, habitaciones, banos, metros, zona, quiere_inmobiliaria, tiene_telefono))

            # Hacemos commit para guardar los cambios
            conn.commit()

            print(f"Inmueble con ID {inmueble_id} agregado correctamente.")
    except Exception as e:
        print("Error en add_propertie:", e)
    finally:
        # Cerramos la conexión
        conn.close()


        # BORRAR TODOS LOS REGISTROS DE inmuebles_todos
def borrar_inmuebles_todos(plataforma, localizacion):
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = """
                DELETE FROM inmuebles_todos 
                WHERE plataforma = %s AND localizacion = %s
            """
            cur.execute(query, (plataforma, localizacion))
            conn.commit()

        print(f"Registros de plataforma '{plataforma}' y localización '{localizacion}' eliminados correctamente.")

    except Exception as e:
        print(f"Error al borrar propiedades: {str(e)}")

    finally:
        if conn:
            conn.close()


# GUARDAR UN INMUEBLE EN inmuebles_todos
def guardar_en_inmuebles_todos(inmueble):
    try:
        conn = get_connection()
        
        insert_query = """
            INSERT INTO inmuebles_todos (id_inmueble, fecha, plataforma, localizacion)
            VALUES (%s, %s, %s, %s)
        """
        
        valores = (
            inmueble['id'],
            inmueble['fecha'],
            inmueble['plataforma'],
            inmueble['localizacion']
        )
        
        with conn.cursor() as cur:
            cur.execute(insert_query, valores)
            conn.commit()  

        print(f"Inmueble {inmueble['id']} guardado correctamente en inmuebles_todos.", flush=True)

    except Exception as e:
        print("Error al guardar inmueble en inmuebles_todos: " + str(e))  # Convertir el error a string

    finally:
        conn.close()  # Asegúrate de cerrar la conexión incluso si ocurre un error

    pass

def obtener_inmuebles_todos(plataforma, localizacion):
    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query = """
                SELECT id_inmueble AS id, fecha, plataforma, localizacion 
                FROM inmuebles_todos 
                WHERE plataforma = %s AND localizacion = %s
            """
            cur.execute(query, (plataforma, localizacion))
            inmuebles = cur.fetchall()

        conn.close()
        return inmuebles

    except Exception as e:
        print(f"Error en obtener_inmuebles_todos: {e}")
        return []

def update_inmueble(datos_inmueble, link):
    try:
        conn = get_connection() 
        with conn.cursor() as cur:
            update_query = """
                UPDATE inmuebles
                SET titulo = %s, fecha = %s, localizacion = %s, plataforma = %s, 
                precio = %s, habitaciones = %s, baños = %s, metros = %s, zona = %s
                WHERE link = %s
            """
            cur.execute(update_query, (datos_inmueble['titulo'], datos_inmueble['fecha'], datos_inmueble['localizacion'], 
                                       datos_inmueble['plataforma'],
                                       datos_inmueble['precio'], datos_inmueble['habitaciones'], datos_inmueble['baños'], 
                                       datos_inmueble['metros'], datos_inmueble['zona'], link))
            conn.commit()
        print("Inmueble actualizado correctamente.")
    except Exception as e:
        print(f"Error al actualizar inmueble: {e}")
    finally:
        conn.close()

