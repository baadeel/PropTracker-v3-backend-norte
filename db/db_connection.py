import psycopg2


def get_connection():
    try:
        connection = psycopg2.connect(
            host="aws-0-eu-central-1.pooler.supabase.com",
            port=6543,
            dbname="postgres",
            user="postgres.dsplygdhezcbdkxkgyih",
            password="QVZTaeAuZA8fG53C",
            sslmode="require"
)

        return connection

    except Exception as e:
        print("Error de conexión con la DB:" + e)
