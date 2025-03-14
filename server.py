from bottle import route, post, run, request, app, static_file, delete
from bottle_cors_plugin import cors_plugin
import json
# import threading
import data
import os
# import time
# import subprocess
from mpd import MPDClient
from musicplayer import MusicPlayer
from urllib.parse import unquote


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


@route('/coverart/<id>')
def coverart(id):
    uri = data.get_uri(con, id)
    cover = player.get_cover_art(uri)

    if not cover == None:
        path = os.path.dirname(cover)
        filename = os.path.basename(cover)
        return static_file(filename, path)


@route('/search')
def search():
    result = data.search(con, request.query.search)
    return json.dumps(result)


@route('/album')
def album():
    search = unquote(request.query.search)
    # sql = "select * from library where album = ? order by artist, album, cast(tracknumber as INT), filename"
    # result = query(sql, (search,))

    result = data.get_album(con, search)

    return json.dumps(result)


@post('/add/<id>')
def add(id):
    uri = data.get_uri(con, id)
    player.add_to_queue(uri)

    return status_json("OK")


@delete('/<id>')
def remove(id):
    player.remove_from_queue(id)

    return status_json("OK")


@delete('/all')
def remove():
    player.clear_queue()
    return status_json("OK")


@route("/queue")
def queue():
    result = player.get_queue()
    return json.dumps(result)


@route("/queuestatus")
def queue():
    result = player.get_queue()
    return f"""{{ "queueCount" : {len(result)}, "queueLength" : {sum([float(x.get("duration")) for x in result])} }}"""


@route("/status")
def status():
    status = player.status()
    uri = status.get("file")
    if uri == None:
        status["libraryid"] = 0
    else:
        status["libraryid"] = data.get_id(con, uri)
    return json.dumps(status)


@post('/play')
def play():
    player.play()
    return status_json("OK")


@post('/stop')
def stop():
    player.stop()
    return status_json("OK")


@post('/skip')
def skip():
    player.skip()
    return status_json("OK")


@post('/pause')
def pause():
    player.pause()
    return status_json("OK")


@post('/queuealbum')
def queuealbum():
    params = request.json
    uri = params["path"][:-1]
    player.add_to_queue(uri)

    return status_json("OK")


@post('/playsong/<id>')
def playsong(id):
    status = player.status()
    if status.get("state") == "play":
        return status_json("Already playing")
    player.clear_queue()
    player.add_to_queue(id)
    player.play()
    return status_json("OK")

# Use for scanning QR codes TODO: Implement


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
    status = player.status()
    if status.get("state") == "play":
        return status_json("Already playing")
    player.clear_queue()
    player.add_album(request.json["album"])
    player.play()
    return status_json("OK")


@post('/rand/<num>')
def random_queue(num):
    con.execute("delete from queue")
    con.execute(
        f"insert into queue(libraryid)  select id from library order by random() limit {num}", ())
    con.commit()
    return """{"status" : "success"}"""


@post('/mix/<name>')
def create_mixtape(name):
    player.save_playlist(name)
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
