import json
import os
import sys
import time
from urllib.parse import unquote
import pathlib
import argparse
from musicbox_mpd import data


def get_args():
    parser = argparse.ArgumentParser(
        prog='Musicbox MPD',
        description='A MPD Client')
    parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('-c', '--configfile')
    parser.add_argument('-s', '--service', action='store_true',
                        help="create systemd service file in current directory")

    parser.add_argument('--create-config', action='store_true',
                        help="create default config file in current directory")
    return parser.parse_args()


async def try_cache_library(player, con):
    backoff = [5, 10, 30, 60, 120]
    for i in range(5):
        try:
            await player.cache_library(con)
            return
        except Exception as e:
            print(f"Error caching library: {e}")
            print(f"Retrying in {backoff[i]} seconds")
            time.sleep(backoff[i])


def add_radio_stations(con, stations):
    # stations = config.get("stations")
    if stations == None:
        return
    data.add_radio_stations(con, stations)


def get_default_config(create=False):
    default_config = """
    {
        "host" : "0.0.0.0",
        "port" : 8080,
        "mpd_host" : "localhost",
        "mpd_port" : 6600,
        "image_folder" : "/tmp/musicbox"
    }
    """
    if create:
        with open("musicbox-mpd.conf.json", "w") as f:
            f.write(default_config)

    return default_config


def get_config(from_arg):
    default_config = get_default_config()
    if from_arg == None:
        config_file = "/etc/musicbox-mpd.conf.json"
    else:
        config_file = from_arg

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


def create_service():
    service_file = f"""
[Unit]
Description=MusicBox MPD Client
After=multi-user.target

[Service]
Type=simple
Restart=always
WorkingDirectory={pathlib.Path(sys.argv[0]).parent.resolve()}
ExecStart={sys.argv[0]}

[Install]
WantedBy=multi-user.target
"""
    with open("musicbox-mpd.service", "w") as f:
        f.write(service_file)

    print("File 'musicbox-mpd.service' created ")
    print("To install musicbox-mpd as a service, run the following commands:")
    print(" sudo mv musicbox-mpd.service /etc/systemd/system/")
    print(" sudo systemctl daemon-reload")
    print(" sudo systemctl enable musicbox-mpd")
    print(" sudo systemctl start musicbox-mpd")
