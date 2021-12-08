import pg8000.dbapi as db
from pg8000 import Connection, DatabaseError, InterfaceError

from config import config

from datetime import datetime


def print_db_version():
    """
    Prints the database version.
    :return bool is connected
    """
    try:
        params = config()
        conn: Connection = db.Connection(**params)
        cur = conn.cursor()
        cur.execute('SELECT version()')
        print('[DB-INFO]: ' + cur.fetchone()[0])
        conn.close()
        return True
    except InterfaceError:
        return False


def create_media_link_table():
    """
    Adds possibly missing tables to the database.
    """
    params = config()
    conn: Connection = db.Connection(**params)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS media_links("
                "id SERIAL PRIMARY KEY,"
                "source TEXT,"
                "title TEXT,"
                "link TEXT UNIQUE)")
    conn.commit()
    cur.close()
    conn.close()


def extend_media_link_table(media: list[dict[str, str]]):
    """
    Adds multiple entries to the media_links table
    """

    updated_rows = len(media)

    for m in media:
        data = (m['source'], m['title'], m['link'])

        try:
            params = config()
            conn: Connection = db.Connection(**params)
            cur = conn.cursor()
            cur.execute("INSERT INTO media_links(source, title, link) VALUES(%s, %s, %s)", data)
            conn.commit()
            cur.close()
            conn.close()
        except DatabaseError:
            updated_rows = updated_rows - 1

    print(f'[INFO]: Added {updated_rows} new entries to media_links.')


def create_motion_table():
    """
    Adds possibly missing tables to the database.
    """
    params = config()
    conn: Connection = db.Connection(**params)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS motions("
                "id SERIAL PRIMARY KEY,"
                "party TEXT,"
                "regarding TEXT,"
                "media TEXT,"
                "status TEXT,"
                "date DATE)")
    conn.commit()
    cur.close()
    conn.close()


def update_motion_table(party: str, regarding: str, media:str, status: str):
    """
    Adds one entry to the motions table
    :return True if new, False if existing
    """
    if media is None:
        data = (party, regarding, status, datetime.utcnow())
    else:
        data = (party, regarding, media, status, datetime.utcnow())

    params = config()
    conn: Connection = db.Connection(**params)
    cur = conn.cursor()

    cur.execute("SELECT status FROM motions WHERE party=%s AND regarding=%s", (party, regarding))
    entries = cur.fetchall()

    if not entries:
        pass
    else:
        if entries[-1][0] == status:
            cur.close()
            conn.close()
            return False

    if media is None:
        cur.execute("INSERT INTO motions(party, regarding, status, date) VALUES(%s, %s, %s, %s)", data)
    else:
        cur.execute("INSERT INTO motions(party, regarding, media, status, date) VALUES(%s, %s, %s, %s, %s)", data)
    conn.commit()
    cur.close()
    conn.close()
    return True
