# musicbox-mpd

A lightweight web based MPD client.

Written in python and vanilla.js.

## Features

- Mobile friendly interface
- Album centred design
- Playback controls: Play, Pause, Stop, Next
- Volume control
- Album art display
- Play queue
- Saved playlist support
- Search on Album, Artist, Song name and Year
- Add any number of random songs to the queue
- Intelligent handling of compilations with multiple artists
- Easy to install with minimal dependencies (just 3 python libraries). Available on snap store.
- Uninterrupted play. UI is designed so it's almost impossible to accidentally click on another song and interrupt what is currently playing.

## Installing/running

Pre-installation
Make sure you have installed and correctly configured MPD

The instuctions below outline how to install and configure on a Debian based linux distribution. It's best to run musicbox-mpd on the same machine as your MPD server.

# Install via the snap store

This is the easiest option as it will also install and configure the services require.

```
sudo apt install snapd
sudo snap install musicbox-mpd
```

You should now be able to browse to http://[name of your MPD server]:8080

# Install via pipx.

If you don't want to install via a snap, you can use pipx and configure the services manually.

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
INFO:     Started server process [32772]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

You can now open a browser on any machine in your local network and enter the following address: http://[name of your MPD server]:8080

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

Musicbox has a very simple UI design. It contains just one textbox, and forgoes any sort of drop down menus. This is so the UI can be written using as little lines of code as possible, making the interface faster and more reliable (less lines of code = less possibility of bugs).

- Pressing the 'search' button with no text in the search box, returns all albums in your collection, ordered by album name.
- Enter text to search for albums, artists or songs.
- Commands always start with a colon. Entering a command in the search box will not search your collection, but perform one of the 9 predefined commands.
- From the start screen, you can click on the command listed at it will pre-populate the search box with that command. Press the "Search" button to execute that command.
- The start screen is displayed when no music is playing. Once you start playing a song, it will display the album art, along with buttons to pause, skip and change the volume.
- If you press "play" on another song while play is in progress, that song will be put next in the queue.
- Unless you press the stop or pause button, the current song will never be interrupted

Commands

- :clear - clear the current queue
- :mix [name of mixtape] - save contents of current queue to a 'mixtape' (aka playlist)
- :delmix [name of mixtape] - delete a mixtape
- :rand [x] - add 'x' number of random songs to the queue
- :update - recan music library
- :settings - show settings screen
- :shuffle - shuffle songs in the current queue
- :error - show the last error message (if any) from the MPD server
- :history - show play history
- :about - display version of musicbox and MPD server
