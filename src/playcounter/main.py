from mpd import MPDClient
from mpd.base import CommandError
import argparse
import time


def get_args():
    parser = argparse.ArgumentParser(
        prog='Playcounter',
        description='Records play counts for songs played on MPD')
    # parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('-s', '--server')
    parser.add_argument('-p', '--port')

    return parser.parse_args()


def get_play_count(client, uri):
    try:
        sticker = client.sticker_get("song", uri, "playCount")

        return int(sticker)
    except CommandError as e:
        return 0
    except ValueError as e:
        return 0


def start():
    print("--- Started watching plays ---")
    args = get_args()
    server = args.server if args.server else "localhost"
    port = args.port if args.port else 6600
    client = MPDClient()
    client.timeout = 10
    client.connect(server, port)
    print(client.mpd_version)
    current_song = ""
    while True:
        print(client.idle('player'))
        status = client.status()
        print(status["state"])
        if status["state"] == "play":
            songs = client.playlistid(status["songid"])
            song = songs[0]
            uri = song["file"]
            if uri != current_song:
                count = get_play_count(client, uri)
                client.sticker_set("song", uri, "playCount", count + 1)
                print(f"Inc count of '{uri}' to {count+1}")
                unix_time = time.time()
                client.sticker_set("song", uri, "lastPlayed", unix_time)
                current_song = uri

        if status["state"] == "stop":
            current_song = ""
