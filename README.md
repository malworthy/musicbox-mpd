# musicbox-mpd

A lightweight web based MPD client.

Written in python and vanilla.js.

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

Pre-installation
Make sure you have installed and correctly configured MPD

The best way to install musicbox-mpd is va pipx. The instuctions below outline how to install and configure on a Debian based linux distribution. It's best to run musicbox-mpd on the same machine as your MPD server.

1. Install pipx (if not already installed)

   ```
   sudo apt install pipx
   ```

2. Install musicbox-mpd

   ```
   pipx install musicbox-mpd
   ```

3. Check that is works
   ```
   musicbox-mpd
   ```

If you all OK you should see output similar to this:

```
0.23.5
Library cached
Bottle v0.12.25 server starting up (using WSGIRefServer())...
Listening on http://localhost:8080/
Hit Ctrl-C to quit.
```

You can now open a browser on any machine in your local network and enter the following address: http://[name of your MPD server]:8080/ui

### Other OS's - Windows/MacOS

Musicbox is just a simple python script, so will work on any OS that supports python. I designed musicbox to run on a raspberrypi, so the installation process on windows is not as user friendly.
For windows you will need to specify the name of the config file, as by default it looks in /etc which will not exist. Also running as a service in windows is beyond the scope of this document.

## Install as a service

Example of installing as a service on a raspberry pi.

1. Create the service file

   ```
   musicbox-mpd --service
   ```

2. Move service file to systemd folder
   ```
   sudo mv musicbox-mpd.service /etc/systemd/system/musicbox-mpd.service
   ```
3. Reload the daemon
   ```
   sudo systemctl daemon-reload
   ```
4. Make sure service gets restarted on reboot
   ```
   sudo systemctl enable musicbox-mpd
   ```
5. Start the service
   ```
   sudo systemctl start musicbox-mpd
   ```
6. Check that it worked
   ```
   sudo systemctl status musicbox-mpd
   ```

## Configuration

By default musicbox looks for the configuration file at /etc/musicbox-mpd.conf.json. This can be over-written by a command line option.

"host" - Ip address musicbox will listen to connections on
"port" - the port musicbox will listen to connections on
"mpd_host" - url of MPD server
"mpd_port" - port of MPD server
"image_folder" - this is the folder musicbox will use to cache album art
"stations" - a list of internet radio stations

## Adding internet radio

Example configuration file containing internet radio stations:

```
{
    "host" : "0.0.0.0",
    "port" : 8080,
    "mpd_host" : "localhost",
    "mpd_port" : 6600,
    "image_folder" : "/tmp/musicbox",
    "stations" : [
        {"name":"3RRR Melbourne", "url":"https://ondemand.rrr.org.au/stream/ws-hq.m3u"},
        {"name": "PBS 106.7FM", "url" : "https://playerservices.streamtheworld.com/api/livestream-redirect/3PBS_FMAAC128.m3u8"}
    ]
}
```

# Command line options

-h, --help  
 show help message and exit

-v, --version  
 display the version number of musicbox

-c CONFIGFILE, --configfile CONFIGFILE  
allows you to specify the name of the config file used. Otherwise will default to /etc/musicbox-mpd.conf.json

-s, --service  
create a systemd service file in current directory

--create-config  
create a default config file in current directory

# User Guide

Commands

- :clear - clear the current queue
- :mix [name of mixtape] - save contents of current queue to a 'mixtape' (aka playlist)
- :delmix [name of mixtape] - delete a mixtape
- :rand [x] - add 'x' number of random songs to the queue
- :update - recan music library
- :settings - show MPD settings
- :shuffle - shuffle songs in the current queue
- :error - show the last error message (if any) from the MPD server
- :about - display version of musicbox and MPD server
