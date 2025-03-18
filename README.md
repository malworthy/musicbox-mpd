# musicbox-mpd

A lightweight web based MPD client.

Written in python and vanilla.js.

This is still a work in progress and it not ready for use yet.

## Features

- Mobile friendly interface
- Album centered design
- Playback controls: Play, Pause, Stop, Next
- Volume control
- Album art display
- Play queue
- Saved playlist support
- Search on Album, Artist, Songname and Year
- Add any number of random songs to the queue
- Intelligent handling of complilations with multiple artists
- Easy to install with minimal dependencies (just 3 python libraries)

## installing/running

Install the following python dependencies:

```
pip install bottle
pip install bottle-cors-plugin
pip install python-mpd2
```

Clone the repository:

```
git clone https://github.com/malworthy/musicbox-mpd.git
```

Create a config.json file:

```
{
    "host" : "0.0.0.0",
    "port" : 8080,
    "mpd_host" : "localhost",
    "mpd_port" : 6600,
    "image_folder" : "/tmp/musicbox",
    "default_image" : "/tmp/musicbox/default.gif",
    "stations" : [
        {"name":"3RRR Melbourne", "url":"https://ondemand.rrr.org.au/stream/ws-hq.m3u"},
        {"name": "PBS 106.7FM", "url" : "https://playerservices.streamtheworld.com/api/livestream-redirect/3PBS_FMAAC128.m3u8"}
    ]
}
```
- Change "host" to "0.0.0.0" to allow remote connections to the server.
- Change "port" if need the server to run on a different port.
- "stations" : list of streaming radio stations (name, url)

```
python server.py
```

Browse to UI:
http://localhost:8080/ui

NOTE: replace 'localhost' with the address of server you are running off.

## Install as a service

Example of installing as a service on a rasperry pi.

1. Create the following file
   sudo nano /etc/systemd/system/musicbox.service

```
[Unit]
Description=MusicBox MPD Client
After=multi-user.target

[Service]
Type=simple
Restart=always
User=pi
WorkingDirectory=/home/pi/code/musicbox-mpd
ExecStart=/home/pi/python-venv/bin/python /home/pi/code/musicbox-mpd/server.py

[Install]
WantedBy=multi-user.target
```

2. Reload the daemon
   sudo systemctl daemon-reload

3. Make sure service gets restarted on reboot
   sudo systemctl enable musicbox

4. Start the service
   sudo systemctl start musicbox

5. Check that it worked
   sudo systemctl status musicbox

# User Guide

Commands

- :clear - clear the current queue
- :mix [name of mixtape] - save contents of current queue to a 'mixtape' (aka playlist)
- :delmix [name of mixtape] - delete a mixtape
- :rand [x] - add 'x' number of random songs to the queue
