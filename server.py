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
    image_folder = config.get("image_folder")

    cover = player.get_cover_art(uri, image_folder)
    if cover == None:
        cover = config.get("default_image")

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
def queuestatus():
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


@post('/playalbum')
def playalbum():
    status = player.status()
    if status.get("state") == "play":
        return status_json("Already playing")
    player.clear_queue()
    uri = request.json["path"][:-1]
    player.add_to_queue(uri)
    player.play()
    return status_json("OK")


@post('/rand/<num>')
def random_queue(num):
    for song in data.get_random_songs(con, num):
        player.add_to_queue(song["filename"])
    return status_json("OK")


@route("/mix")
def get_mixtapes():
    result = player.get_playlists()
    return json.dumps(result)


@post('/loadmix/<name>')
def load_mixtape(name):
    player.load_playlist(name)
    return status_json("OK")


@post('/savemix/<name>')
def load_mixtape(name):
    player.update_playlist(name)
    return status_json("OK")


@post('/mix/<name>')
def create_mixtape(name):
    player.save_playlist(name)
    return status_json("OK")


@delete('/mix/<name>')
def delete_mixtape(name):
    player.delete_playlist(name)
    return status_json("OK")


##### ENTRY POINT #####
con = data.in_memory_db()

f = open("config.json")
config = json.load(f)
f.close()

app = app()
app.install(cors_plugin('*'))
player = MusicPlayer(config["mpd_host"], config["mpd_port"])
player.cache_library(con)
run(host=config["host"], port=config["port"])
