from collections import namedtuple
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor



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
                # Kalau ga error, return hasil SELECT
                hasil = map_cursor(cursor)
            else:
                # Kalau ga error, return jumlah row yang termodifikasi oleh INSERT, UPDATE, DELETE
                hasil = cursor.rowcount
                connection.commit()
        except Exception as e:
            # Ga tau error apa
            hasil = "error :\n" + str(e)

    return hasil

email = "ganjar@pranowo.com"
id_konten = "f178a9c2-9054-4fe2-8972-77abc0998131"
# email_exists = query(f"""
#     SELECT * FROM 
#         (SELECT * FROM SONG WHERE id_konten = '{id_konten}') AS LAGU 
#         NATURAL JOIN 
#         (SELECT judul AS judul_lagu, tanggal_rilis, tahun, durasi FROM KONTEN WHERE id = '{id_konten}') AS CONTENT
#         JOIN
#         (SELECT id AS album_id, judul AS judul_album FROM ALBUM) AS ALBUM ON LAGU.id_album = ALBUM.album_id
#         JOIN 
#         (SELECT id AS artist_id, email_akun FROM ARTIST) AS ARTIST ON LAGU.id_artist = ARTIST.artist_id
#         JOIN
#         (SELECT email, nama FROM AKUN) AS AKUN ON ARTIST.email_akun = AKUN.email;
#     """)
# print(email_exists)
# songwriters = query(f"""
#     SELECT nama FROM AKUN WHERE email IN 
#         (SELECT email_akun FROM SONGWRITER WHERE id IN
#             (SELECT id_songwriter FROM SONGWRITER_WRITE_SONG WHERE id_song = '{id_konten}')
#         )
# """)

# print(songwriters)

# songwriters = [sw['nama'] for sw in songwriters]

# print(songwriters)

id_user_playlist = "05a104c1-e02b-4dff-bfc1-d52c92ba6ed2"
query_string = f"""
    SELECT *
    FROM USER_PLAYLIST up
    JOIN AKUN a ON up.email_pembuat = a.email
    WHERE up.id_user_playlist = '{id_user_playlist}';        
"""
playlist = query(query_string)[0]
# query_string = f"""
#     SELECT * FROM 
#     (SELECT * FROM SONG WHERE id_konten IN
#         (SELECT id_song FROM PLAYLIST_SONG WHERE id_playlist = '{playlist['id_playlist']}')) AS LAGU
#     JOIN
#     (SELECT id, judul AS judul_lagu, tanggal_rilis, tahun, durasi FROM KONTEN) AS CONTENT
#     ON LAGU.id_konten = CONTENT.id
#     JOIN
#     (SELECT id AS artist_id, email_akun FROM ARTIST) AS ARTIST ON LAGU.id_artist = ARTIST.artist_id
        
# """
# songs = query(query_string)
# for song in songs:
#     print(song)
#     print("=========")
# print(len(songs))
print(playlist)
print([1,2,3]+[4,5,6])