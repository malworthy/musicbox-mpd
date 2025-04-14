from mpd import MPDClient
from mpd.base import CommandError
import argparse
import time
import os
import pathlib
import json


def get_args():
    parser = argparse.ArgumentParser(
        prog='playcounter-mpd',
        description='Records play counts for songs played on MPD')
    parser.add_argument('-s', '--server')
    parser.add_argument('-p', '--port')
    parser.add_argument('--password')

    return parser.parse_args()


def get_config():
    default_config = """
    {
        "mpd_host" : "localhost",
        "mpd_port" : 6600
    }
    """
    folder = os.environ.get("SNAP_COMMON")
    if folder == None:
        folder = "/etc"
    config_file = os.path.join(folder, "musicbox-mpd.conf.json")

    if pathlib.Path(config_file).is_file():
        try:
            f = open(config_file)
            config = json.load(f)
            f.close()
            return config
        except Exception as e:
            print(f"Error loading config file: {e}")

    print("No config file found, using defaults")
    return json.loads(default_config)


def get_play_count(client, uri):
    try:
        sticker = client.sticker_get("song", uri, "playCount")

        return int(sticker)
    except CommandError as e:
        return 0
    except ValueError as e:
        return 0


def main_loop():
    print("--- Started watching plays ---")
    args = get_args()
    config = get_config()
    server = args.server if args.server else config["mpd_host"]
    port = args.port if args.port else config["mpd_port"]
    password = args.password if args.password else config.get("password")
    client = MPDClient()
    client.timeout = 10
    if password != None:
        client.password(password)
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


def start():
    backoff = [5, 5, 5, 60 * 5, 60 * 30]
    error_count = 0
    while True:
        try:
            main_loop()
        except Exception as e:
            print(f"Error: {e}")
            print(f"Retrying in {backoff[error_count]} seconds")
            time.sleep(backoff[error_count])
            error_count += 1
            if error_count >= len(backoff):
                error_count = len(backoff) - 1
        except KeyboardInterrupt:
            print("Exiting...")
            break


if __name__ == "__main__":
    start()
