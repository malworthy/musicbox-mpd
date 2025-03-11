import sqlite3


def create_connection():
    connection = sqlite3.connect("musiclibrary.db")
    connection.row_factory = sqlite3.Row

    return connection


def get_next_song(db_conn):
    get_song_sql = """select q.id, l.filename, l.id as libraryid 
            from queue q inner join library l on q.libraryid = l.id 
            where canplay = 1 and playing is null order by q.id limit 1"""
    curs = db_conn.execute(get_song_sql)
    result = curs.fetchone()
    return result


def setplaying(id, db_conn):
    curs = db_conn.execute(
        "select count(*) from queue where playing is not null")
    is_playing = curs.fetchone()
    if is_playing[0] > 0:
        print("Attempting to set 2 songs as playing at once")
        return

    db_conn.execute(
        "update queue set playing = datetime('now') where id = ?", (id,))

    sql = """insert into history(libraryid, dateplayed) 
             select libraryid, playing 
             from queue 
             where playing is not null"""
    db_conn.execute(sql)
    db_conn.commit()


def is_paused(db_conn):
    curs = db_conn.execute(
        "select count(*) from queue where playing is not null and canplay = 1")
    result = curs.fetchone()
    return result[0] > 0


def get_radio_url(db_conn, id):
    curs = db_conn.execute(
        "select url from radio where id = ?", (id,))
    result = curs.fetchone()
    return result[0]


def reset_queue(db_conn):
    db_conn.execute("update queue set playing = null, canplay = 1")
    db_conn.commit()
