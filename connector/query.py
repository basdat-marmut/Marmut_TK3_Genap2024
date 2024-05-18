from collections import namedtuple
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from django.http import HttpRequest  # for the 'request' parameter


try:
    connection = psycopg2.connect(user="postgres.tutzylpjrcjropovgoly",
                        password="eqRvUiBE4LZlukUp",
                        host="aws-0-ap-southeast-1.pooler.supabase.com",
                        port="5432",
                        database="postgres")

    # Create a cursor to perform database operations
    connection.autocommit = True
    cursor = connection.cursor()
except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)


def map_cursor(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple("Result", [col[0] for col in desc])
    return [dict(row) for row in cursor.fetchall()]

def query(query_str: str):
    hasil = []
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SET SEARCH_PATH TO PUBLIC")
        try:
            cursor.execute(query_str)
            if query_str.strip().upper().startswith("SELECT"):
                hasil = map_cursor(cursor)
            else:
                hasil = cursor.rowcount
                connection.commit()
        except Exception as e:
            hasil = "error :\n" + str(e)
    return hasil

def get_session_info(request):
    session_id = request.COOKIES.get('session_id')
    if session_id:
        user = query(f"SELECT * FROM SESSIONS WHERE session_id = '{session_id}'")
        if user:
            return user[0]
    return None

def get_navbar_info(request: HttpRequest):
    session_info = get_session_info(request)

    if session_info:
        return {
            'is_guest': False,
            'is_user': not session_info['is_label'],
            'is_artist': session_info['is_artist'],
            'is_songwriter': session_info['is_songwriter']  ,
            'is_podcaster': session_info['is_podcaster'],
            'is_premium': session_info['is_premium'],
            'is_label': session_info['is_label'],
        }
    else:
        return {
            'is_guest': True,
            'is_user': False,
            'is_artist': False,
            'is_songwriter': False,
            'is_podcaster': False,
            'is_premium': False,
            'is_label': False,
        }
