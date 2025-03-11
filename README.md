# musicbox-mpd

A lightweight music server for playing local files, with a retro user interface. Like mopidy but without the streaming. Perfect for running on a raspberry pi.

Written in python and vanilla.js.

## installing/running

Install the following python dependencies:

```
pip install bottle
pip install bottle-cors-plugin
pip install pygame
pip install music-tag
```

You may also need install some additional libraries (command for debian based systems):

```
sudo apt-get install libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0
```

Clone the repository:

```
git clone https://github.com/malworthy/musicbox.git
```

Create a config.json file:

```
{
    "library" : "/path/to/library/",
    "host" : "localhost",
    "port" : 8080,
    "extensions" : ["mp3", "flac"],
    "radio_player": "mplayer",
    "stations" : [
        {"name":"3RRR Melbourne", "url":"https://ondemand.rrr.org.au/stream/ws-hq.m3u"},
        {"name": "PBS 106.7FM", "url" : "https://playerservices.streamtheworld.com/api/livestream-redirect/3PBS_FMAAC128.m3u8"}
    ]
}
```

- Change "library" to point to your music library.
- Change "host" to "0.0.0.0" to allow remote connections to the server.
- Change "port" if need the server to run on a different port.
- Supported audio formats: mp3, ogg, wav and flac.
- "radio_player" : application used to play streams e.g. mplayer, cvlc
- "stations" : list of streaming radio stations (name, url)

Update database with library:

```
python update_library.py --all
```

To add radio stations to the library:

```
python update_library.py --stations
```

Run the server:

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
Description=MusicBox Music Server
After=multi-user.target

[Service]
Type=simple
Restart=always
User=pi
WorkingDirectory=/home/pi/code/musicbox
ExecStart=/usr/bin/python3 /home/pi/code/musicbox/server.py

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
- :hist - show history of songs played
