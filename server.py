from bottle import route, post, run, request, app, static_file, delete
from bottle_cors_plugin import cors_plugin
import json
import threading
# from pygame import mixer
# import pygame
# from player import playasync
from data import create_connection, get_next_song, setplaying
import data
import data
import os
import time
import subprocess
from mpd import MPDClient
from musicplayer import MusicPlayer


def query(sql, params):
    res = con.execute(sql, params)
    rows = res.fetchall()
    return [dict(row) for row in rows]


def status_json(msg):
    return """{"status": "_*_"}""".replace("_*_", msg)


@route('/ui')
def ui():
    return static_file("ui.html", "./ui/")


@route('/ui/<file>')
def ui2(file):
    return static_file(file, "./ui/")


@route('/radio/play/<id>')
def radio(id):
    global radio_process
    if radio_process != None:
        return "radio already playing"

    app = config["radio_player"]
    url = data.get_radio_url(con, id)
    radio_process = subprocess.Popen([app, url])
    return status_json(f"radio play started {radio_process.pid}")


@route('/radio/stop')
def stop_radio():
    global radio_process
    if radio_process == None:
        return status_json("radio is not playing so can't stop it")
    pid = radio_process.pid
    radio_process.kill()
    radio_process = None
    return f"radio has stopped playing.  pid={pid}"


@route('/radio/list')
def list_radio():
    sql = "select id, name from radio"
    result = query(sql, ())
    return json.dumps(result)


@route('/coverart/<id>')
def coverart(id):
    result = query(
        "select coverart from library where id = ? and coverart is not null", (id,))
    if len(result) > 0:
        path = os.path.dirname(result[0]["coverart"])
        filename = os.path.basename(result[0]["coverart"])
        return static_file(filename, path)


@route('/search')
def search():
    include_songs = len(request.query.search) > 1
    x = f"%{request.query.search}%"
    print(x)
    sql = """
        select album, case when count(*) > 1 then 'Various' else max(albumartist) end artist, null as tracktitle, 0 as id, 0 as length 
        from (select distinct coalesce(albumartist, artist) as albumartist, album 
        from library where album like ? or artist like ? or albumartist like ?) sq 
        group by album       
    """

    if include_songs:
        sql += """
            union 
            select album, artist, tracktitle, id, length
            from library
            where tracktitle like ?"""

    sql += "order by tracktitle, artist;"

    if include_songs:
        result = query(sql, (x, x, x, x))
    else:
        result = query(sql, (x, x, x))

    return json.dumps(result)


@route('/album')
def album():
    search = request.query.search
    sql = "select * from library where album = ? order by artist, album, cast(tracknumber as INT), filename"
    result = query(sql, (search,))

    return json.dumps(result)


@post('/add/<id>')
def add(id):
    sql = "select filename from library where id = ?"
    result = query(sql, (id,))
    uri = result[0]["filename"]
    player.add_to_queue(uri)

    result = query("select 1 as queueCount from library", ())  # placeholder
    return json.dumps(result[0])


@delete('/<id>')
def remove(id):
    params = request.json
    player.remove_from_queue(id)

    result = query("select 1 as queueCount from library", ())  # placeholder
    return json.dumps(result[0])


@delete('/all')
def remove():
    sql = "delete from queue"
    con.execute(sql)
    con.commit()
    return """{ "queueCount" : 0 }"""


@route("/queue")
def queue():
    result = player.get_queue()
    return json.dumps(result)


@route("/wrapped/song/<year>")
def wrapped(year):
    sql = f"""
        select l.tracktitle || ' - ' || l.artist as song, count(*) as plays
        from history h
        inner join library l on h.libraryid = l.id
        where strftime('%Y', h.dateplayed) = ?
        group by l.tracktitle,l.artist
        order by plays
        desc limit 5;
    """
    result = query(sql, (year,))
    return json.dumps(result)


@route("/wrapped/artist/<year>")
def wrapped(year):
    sql = f"""
        select l.artist, count(*) as plays
        from history h
        inner join library l on h.libraryid = l.id
        where strftime('%Y', h.dateplayed) = ?
        group by l.artist
        order by plays
        desc limit 5;
    """
    result = query(sql, (year,))
    return json.dumps(result)


@route("/wrapped/album/<year>")
def wrapped(year):
    sql = f"""
        select l.album || ' - ' || l.artist as album, count(*) as plays
        from history h
        inner join library l on h.libraryid = l.id
        where strftime('%Y', h.dateplayed) = ?
        group by l.album, l.artist
        order by plays
        desc limit 5;
    """
    result = query(sql, (year,))
    return json.dumps(result)


@route("/wrapped/time/<year>")
def wrapped(year):
    sql = f"""
        select sum(l.length) as seconds
        from history h
        inner join library l on h.libraryid = l.id
        where strftime('%Y', h.dateplayed) = ?
    """
    result = query(sql, (year,))
    return json.dumps(result[0])


@route("/queuestatus")
def queue():
    result = player.get_queue()
    return f"""{{ "queueCount" : {len(result)}, "queueLength" : {sum([float(x.get("duration")) for x in result])} }}"""


@route("/history")
def history():
    sql = """
        select datetime(dateplayed,'localtime') as dateplayed, l.artist, l.tracktitle, l.album 
        from history h 
        inner join library l on l.id = h.libraryid 
        order by dateplayed desc;
    """
    return json.dumps(query(sql, ()))


@route("/status")
def status():
    return """
           { "playing": 2, "desc" : "No implemented yet" }
        """


@post('/play')
def play():
    player.play()
    return """{"status" : "play started", "id" : """ + f"{0}" + "}"


@post('/stop')
def stop():
    con.execute("update queue set canplay = 0")
    con.execute("delete from queue where playing is not null")
    con.commit()
    # mixer.music.stop()
    return """{"status" : "stopped"}"""


@post('/skip')
def skip():
    stop()
    time.sleep(1)
    return play()


@post('/pause')
def pause():
    # if mixer.music.get_busy():
    #    mixer.music.pause()
    #    return """{"paused" : true}"""
    # else:
    #    mixer.music.unpause()
    return """{"paused" : false}"""


@post('/queuealbum')
def queuealbum():
    params = request.json
    con.execute(
        "insert into queue(libraryid, canplay) select id, 1 from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    return """{"status" : "queued"}"""


@post('/playsong/<id>')
def playsong(id):
    print("*** in playsong ***")
    # if mixer.music.get_busy():
    #    return """{"status" : "already playing"}"""
    con.execute("delete from queue")
    add(id)
    return play()


@route('/autoplay/<album>')
def autoplay(album):
    # is_playing = mixer.music.get_busy()
    # if not is_playing:
    #    con.execute("delete from queue")

    con.execute(
        "insert into queue(libraryid) select id from library where album = ? and id not in (select libraryid from queue) order by cast(tracknumber as INT), filename", (album,))
    con.commit()

    message = f"The album {album} has been added to the queue"
    # if not is_playing:
    #    play()
    #    message = f"Playing album {album}"

    return f'<html><body><div style="text-align: center"><h2>{message}</h2><a href="/ui">Click here for MusicBox</a></div></body></html>'

    # return static_file("ui.html", "./ui/")


@post('/playalbum')
def playalbum():
    # if mixer.music.get_busy():
    #    return """{"status" : "already playing"}"""

    params = request.json
    con.execute("delete from queue")
    con.execute(
        "insert into queue(libraryid) select id from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    return play()


@post('/rand/<num>')
def random_queue(num):
    con.execute("delete from queue")
    con.execute(
        f"insert into queue(libraryid)  select id from library order by random() limit {num}", ())
    con.commit()
    return """{"status" : "success"}"""


@post('/mix/<name>')
def create_mixtape(name):
    sql = """
        insert into library(filename, tracktitle, artist, album, albumartist, tracknumber, length, year)
        select l.filename, l.tracktitle,l.artist, ? as album, 'mixtape' as albumartist, q.id, l.length, l.year 
        from queue q inner join library l on q.libraryid = l.id;
    """
    con.execute(
        "delete from library where albumartist = 'mixtape' and album = ?", (name,))
    con.execute(sql, (name,))
    con.commit()
    return """{"status" : "success"}"""


@delete('/mix/<name>')
def delete_mixtape(name):
    con.execute(
        "delete from library where albumartist = 'mixtape' and album = ?", (name,))
    con.commit()
    return """{"status" : "success"}"""


def cache_library():
    print("Caching library")
    client = MPDClient()
    client.timeout = 10
    client.connect("musicbox", 6600)
    print(client.mpd_version)
    songs = client.search("any", "")
    result = [(x.get("file"), x.get("title"), x.get("artist"), x.get("album"), x.get(
        "albumartist"), x.get("track"), x.get("time"), x.get("date")) for x in songs]
    client.disconnect()
    try:
        con.execute("create table library(id INTEGER PRIMARY KEY, filename text, tracktitle text, artist text, album text, albumartist text, tracknumber int, length int, year text)")
    except:
        print("Library table already exists")
    con.executemany(
        "insert into library(filename,tracktitle,artist, album, albumartist, tracknumber, length, year) values (?,?,?,?,?,?,?,?)", result)
    print("Library cached")
    # cur = con.cursor()
    # xxx = query("select * from library limit 100", ())
    # print(xxx)


##### ENTRY POINT #####
con = data.in_memory_db()
player = MusicPlayer()

radio_process = None

f = open("config.json")
config = json.load(f)
f.close()

app = app()
app.install(cors_plugin('*'))
# pygame.init()
# mixer.init()

# client = MPDClient()
# client.connect("musicbox", 6600)

# print(client.mpd_version)
cache_library()
run(host=config["host"], port=config["port"])
