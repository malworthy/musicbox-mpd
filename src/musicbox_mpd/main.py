from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse, HTMLResponse
from starlette.routing import Route
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.background import BackgroundTask
from urllib.parse import unquote
# import asyncio
import uvicorn
import os
import pathlib
import contextlib
# import json

from musicbox_mpd.musicplayer import MusicPlayer
from musicbox_mpd import data
from musicbox_mpd import __about__
from musicbox_mpd import startup


def get_static_path():
    return os.path.join(pathlib.Path(__file__).parent.resolve(), "ui")


def status_json(status, message=""):
    return {"status": status, "message": message}


def homepage(request):
    with open(os.path.join(get_static_path(), "ui.html")) as f:
        html = f.read()
        return HTMLResponse(html.replace("{ver}", __about__.__version__))


async def get_version(request):
    return JSONResponse({'musicbox': __about__.__version__, 'mpd': await player.get_mpd_version()})


async def status(request):
    status = await player.status()
    uri = status.get("file")
    if uri == None:
        status["libraryid"] = 0
    else:
        status["libraryid"] = data.get_id(con, uri)
    return JSONResponse(status)


async def play(request):
    status = await player.play()
    if status == False:
        return JSONResponse(status_json("Error", await player.error_message))
    return JSONResponse(status_json("OK"))


async def stop(request):
    await player.stop()
    return JSONResponse(status_json("OK"))


async def search(request):
    search_text = request.query_params["search"]
    result = data.search(con, search_text)

    # If no results and no search filters, try to cache the library and search again
    if len(result) == 0 and search_text == "":
        print("Library empty - Caching library and retrying search")
        await player.cache_library(con)
        result = data.search(con, search_text)

    return JSONResponse(result)


async def queuestatus(request):
    result = await player.get_queue()
    return JSONResponse({"queueCount": len(result), "queueLength": sum([float(x.get("duration")) for x in result if x.get("duration") != None])})


async def coverart(request):
    id = request.path_params["id"]
    uri = data.get_uri(con, id)
    default_image = os.path.join(get_static_path(), "default.gif")

    if uri == None:
        return FileResponse(default_image)

    image_folder = config.get("image_folder")
    cover = await player.get_cover_art(uri, image_folder)

    if cover == None:
        return FileResponse(default_image)

    if not cover == None:
        path = os.path.dirname(cover)
        filename = os.path.basename(cover)
        return FileResponse(os.path.join(path, filename))


def album(request):
    search = unquote(request.query_params["search"])
    result = data.get_album(con, search)

    return JSONResponse(result)


async def add(request):
    id = request.path_params["id"]
    uri = data.get_uri(con, id)
    await player.add_to_queue(uri)

    return JSONResponse(status_json("OK"))


async def remove(request):
    id = request.path_params["id"]
    await player.remove_from_queue(id)

    return JSONResponse(status_json("OK"))


async def remove_all(request):
    await player.clear_queue()
    return JSONResponse(status_json("OK"))


async def queue(request):
    result = await player.get_queue()
    return JSONResponse(result)


async def skip(request):
    await player.skip()
    return JSONResponse(status_json("OK"))


async def pause(request):
    await player.pause()
    return JSONResponse(status_json("OK"))


async def volume(request):
    vol = request.path_params["vol"]
    result = await player.volume(vol)
    return JSONResponse(status_json(result))


async def queuealbum(request):
    params = await request.json()
    uri = params["path"][:-1]
    await player.add_to_queue(uri)

    return JSONResponse(status_json("OK"))


async def playsong(request):
    id = request.path_params["id"]
    status = await player.status()
    if status.get("state") == "play":
        return JSONResponse(status_json("Already playing"))
    uri = data.get_uri(con, id)
    await player.clear_queue()
    await player.add_to_queue(uri)
    if not await player.play():
        return JSONResponse(status_json("Error", player.error_message))
    return JSONResponse(status_json("OK"))

# Use for scanning QR codes TODO: Implement


async def playalbum(request):
    status = await player.status()
    if status.get("state") == "play":
        return JSONResponse(status_json("Already playing"))
    await player.clear_queue()
    json = await request.json()
    uri = json["path"][:-1]
    await player.add_to_queue(uri)
    await player.play()
    return JSONResponse(status_json("OK"))


async def random_queue(request):
    num = request.path_params["num"]
    for song in data.get_random_songs(con, num):
        await player.add_to_queue(song["filename"])
    return JSONResponse(status_json("OK"))


async def get_mixtapes(request):
    result = await player.get_playlists()
    return JSONResponse(result)


async def load_mixtape(request):
    name = request.path_params["name"]
    await player.load_playlist(name)
    return JSONResponse(status_json("OK"))


async def save_mixtape(request):
    name = request.path_params["name"]
    await player.update_playlist(name)
    return JSONResponse(status_json("OK"))


async def create_mixtape(request):
    name = request.path_params["name"]
    result = await player.save_playlist(name)
    if result:
        return JSONResponse(status_json("OK"))
    else:
        return JSONResponse(status_json("Error", player.error_message))


async def delete_mixtape(request):
    name = request.path_params["name"]
    await player.delete_playlist(name)
    return JSONResponse(status_json("OK"))


async def update(request):
    task = BackgroundTask(player.wait_for_update, con)
    result = await player.update(con)
    return JSONResponse(result, background=task)


async def setting(request):
    name = request.path_params["name"]
    value = request.path_params["value"]
    await player.set_setting(name, value)
    return JSONResponse(status_json("OK"))


async def replaygain(request):
    result = await player.get_replay_gain_status()
    if result == None:
        return JSONResponse(status_json("Error", player.error_message))
    return JSONResponse(status_json("OK", result))


async def set_replaygain(request):
    json = await request.json()
    value = json["mode"]
    result = await player.set_replay_gain_mode(value)
    if result == False:
        return JSONResponse(status_json("Error", player.error_message))
    return JSONResponse(status_json("OK", result))


async def shuffle(request):
    result = await player.shuffle()
    if result == False:
        return JSONResponse(status_json("Error", player.error_message))
    return JSONResponse(status_json("OK", result))


@contextlib.asynccontextmanager
async def lifespan(app):
    print("Run at startup!")
    await startup.try_cache_library(player, con)
    startup.add_radio_stations(con, config.get("stations"))
    yield
    print("Run on shutdown!")

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/remove/{id}', remove, methods=['DELETE']),
    Route('/version', get_version),
    Route('/status', status),
    Route('/queuestatus', queuestatus),
    Route('/play', play, methods=['POST']),
    Route('/stop', stop, methods=['POST']),
    Route('/search', search),
    Route('/coverart/{id}', coverart),
    Route('/album', album),
    Route('/add/{id}', add, methods=['POST']),
    Route('/all', remove_all, methods=['DELETE']),
    Route('/queue', queue),

    Route('/playalbum', playalbum, methods=['POST']),
    Route('/queuealbum', queuealbum, methods=['POST']),
    Route('/playsong/{id}', playsong, methods=['POST']),
    Route('/rand/{num}', random_queue, methods=['POST']),
    Route('/mix', get_mixtapes),
    Route('/loadmix/{name}', load_mixtape, methods=['POST']),
    Route('/savemix/{name}', save_mixtape, methods=['POST']),
    Route('/mix/{name}', create_mixtape, methods=['POST']),
    Route('/mix/{name}', delete_mixtape, methods=['DELETE']),
    Route('/update', update, methods=['POST']),
    Route('/setting/{name}/{value}', setting, methods=['POST']),
    Route('/replaygain', replaygain, methods=['GET']),
    Route('/replaygain', set_replaygain, methods=['POST']),
    Route('/shuffle', shuffle, methods=["POST"]),

    Route('/skip', skip, methods=['POST']),
    Route('/pause', pause, methods=['POST']),
    Route('/volume/{vol}', volume, methods=['POST']),

    Mount('/ui', app=StaticFiles(directory=get_static_path()), name="ui"),
], lifespan=lifespan)

args = startup.get_args()
config = startup.get_config(args.configfile)
con = data.in_memory_db()
player = MusicPlayer(config["mpd_host"], config["mpd_port"])


def start():
    if args.service:
        startup.create_service()
        return

    if args.version:
        print(f"Musicbox MPD version {__about__.__version__}")
        return

    if args.create_config:
        startup.get_default_config(True)
        print("Config file 'musicbox-mpd.conf.json' created")
        return

    uvicorn.run("musicbox_mpd.main:app",
                host=config["host"], port=config["port"], reload=True)
