from mpd.asyncio import MPDClient
from threading import Thread
import os
import mpd
import time


class MusicPlayer:

    def __init__(self, host="localhost", port=6600):
        self.host = host
        self.port = port
        self.client = None  # self.create_client()

    """ Check if the client is connected to the server, if not, connect """

    async def connect(self):
        if self.client == None:
            self.client = self.create_client()
            await self.client.connect(self.host, self.port)
            return

        try:
            await self.client.ping()
        except mpd.ConnectionError as e:
            print(f"Reconnecting to server: {e}")
            await self.client.connect(self.host, self.port)
        except Exception as e:
            print(f"Exception occurred connecting: {e}")

    def create_client(self):
        client = MPDClient()
        client.timeout = 10
        client.idletimeout = None
        return client

    async def cache_library(self, con):
        await self.connect()
        print(self.client.mpd_version)
        songs = await self.client.search("any", "")
        result = [(x.get("file"), x.get("title"), x.get("artist"), x.get("album"), x.get(
            "albumartist"), x.get("track"), x.get("time"), x.get("date")) for x in songs]

        con.execute("delete from library where radio != 1")
        con.executemany(
            "insert into library(filename,tracktitle,artist, album, albumartist, tracknumber, length, year) values (?,?,?,?,?,?,?,?)", result)
        print("Library cached")

    async def get_mpd_version(self):
        try:
            await self.connect()
            return self.client.mpd_version
        except Exception as e:
            print(f"Error getting MPD version: {e}")
            self.error_message = str(e)
            return "Error getting MPD version"

    async def add_to_queue(self, uri):
        try:
            await self.connect()
            await self.client.add(uri)
        except Exception as e:
            print(f"Error adding song to queue: {e}")
            self.error_message = str(e)
            return False
        return True

    async def play_next(self, uri, status):
        try:
            await self.connect()
            # status = await self.client.status()
            song = status.get("song")
            await self.client.addid(uri, int(song) + 1)
        except Exception as e:
            print(f"Error adding song to queue: {e}")
            self.error_message = str(e)
            return False
        return True

    async def remove_from_queue(self, id):
        try:
            await self.connect()
            await self.client.deleteid(id)
        except Exception as e:
            print(f"Error removing song from queue: {e}")
            self.error_message = str(e)
            return False
        return True

    async def clear_queue(self):
        try:
            await self.connect()
            await self.client.clear()
        except Exception as e:
            print(f"Error clearing queue: {e}")
            self.error_message = str(e)
            return False
        return True

    async def get_queue(self):
        try:
            await self.connect()
            queue = await self.client.playlistinfo()
        except Exception as e:
            print(f"Error getting queue: {e}")
            self.error_message = str(e)
            return []
        return queue

    async def clear_queue(self):
        try:
            await self.connect()
            await self.client.clear()
        except Exception as e:
            print(f"Error clearing queue: {e}")
            self.error_message = str(e)
            return False
        return True

    async def play(self):
        try:
            await self.connect()
            await self.client.play(0)
        except Exception as e:
            print(f"Error playing song: {e}")
            self.error_message = str(e)
            return False
        return True

    async def stop(self):
        try:
            await self.connect()
            await self.client.stop()
        except Exception as e:
            print(f"Error stopping song: {e}")
            return False
        return True

    async def status(self):
        try:
            await self.connect()
            s = await self.client.status()
            songid = s.get("songid")
            result = s
            if songid != None:
                d = await self.client.playlistid(songid)

                if len(d) > 0:
                    result["title"] = d[0].get("title")
                    result["artist"] = d[0].get("artist")
                    result["file"] = d[0].get("file")
            return result
        except Exception as e:
            print(f"Error getting status: {e}")
            return {}

    async def pause(self):
        try:
            print("in pause")
            await self.connect()
            s = await self.client.status()
            state = s.get("state")
            if state == "pause":
                await self.client.pause(0)
            else:
                await self.client.pause(1)
        except Exception as e:
            print(f"Error pausing song: {e}")
            return False
        return True

    async def volume(self, vol):
        try:
            await self.connect()
            await self.client.volume(vol)
            s = await self.client.status()
            return s.get("volume")
        except Exception as e:
            print(f"Error setting volume: {e}")
            return "Cannot set volume"

    async def get_cover_art(self, uri, img_folder):
        if img_folder == None:
            return None
        try:
            if os.path.exists(img_folder) == False:
                os.makedirs(img_folder)
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None

        try:
            folder = os.path.dirname(uri)
            folder = folder.replace("/", "-").replace("\\", "-")
            filename = "_" + "".join(
                x for x in folder if x.isalnum() or x == "-") + ".jpg"
            filename = os.path.join(img_folder, filename)
            if os.path.exists(filename):
                return filename

            await self.connect()
            img = await self.client.readpicture(uri)
            if img.get("binary") == None:
                print("embedded art not found - looking up albumart")
                img = await self.client.albumart(uri)

            with open(filename, "wb") as file:
                file.write(img["binary"])
            return filename
        except Exception as e:
            print(f"Error getting cover art: {e}")
            return None

    async def skip(self):
        try:
            await self.connect()
            await self.client.next()
        except Exception as e:
            print(f"Error skipping song: {e}")
            return False
        return True

    async def save_playlist(self, name):
        try:
            await self.connect()
            await self.client.save(name)
        except Exception as e:
            print(f"Error saving playlist: {e}")
            self.error_message = str(e)
            return False
        return True

    async def update_playlist(self, name):
        try:
            await self.connect()
            await self.client.rm(name)
            await self.client.save(name)
        except Exception as e:
            print(f"Error updating playlist: {e}")
            return False
        return True

    async def delete_playlist(self, name):
        try:
            await self.connect()
            await self.client.rm(name)
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False
        return True

    async def get_playlists(self):
        try:
            await self.connect()
            playlists = await self.client.listplaylists()
        except Exception as e:
            print(f"Error getting playlists: {e}")
            return []
        return playlists

    async def load_playlist(self, name):
        try:
            await self.connect()
            await self.client.load(name)
        except Exception as e:
            print(f"Error loading playlist: {e}")
            return False
        return True

    async def update(self, con):
        try:
            await self.connect()
            status = await self.client.status()
            updating = status.get("updating_db")
            if updating != None:
                return updating

            result = await self.client.update()
            # thread = Thread(target=self.wait_for_update, args=(con, ))
            # thread.start()
        except Exception as e:
            print(f"Error updating library: {e}")
            return None
        return result

    async def wait_for_update(self, con):
        try:
            local_client = self.create_client()
            await local_client.connect(self.host, self.port)

            print("Waiting for update")
            async for subsystem in local_client.idle():
                print("Idle change in ", subsystem)
                if "update" in subsystem:
                    status = await local_client.status()
                    updating = status.get("updating_db")
                    print(f"Updating: {updating}")
                    if updating == None:
                        await self.cache_library(con)
                        return True

        except Exception as e:
            print(f"Error waiting for update: {e}")
            return False
        finally:
            local_client.disconnect()
        return False

    async def set_setting(self, name, value):
        try:
            await self.connect()
            if name == "random":
                await self.client.random(value)
            elif name == "repeat":
                await self.client.repeat(value)
            elif name == "consume":
                await self.client.consume(value)
        except Exception as e:
            print(f"Error setting value: {e}")
            return False

    async def get_replay_gain_status(self):
        try:
            await self.connect()
            return await self.client.replay_gain_status()
        except Exception as e:
            print(f"Error getting replay gain status: {e}")
            self.error_message = str(e)
            return None

    async def set_replay_gain_mode(self, mode):
        try:
            await self.connect()
            await self.client.replay_gain_mode(mode)
            return True
        except Exception as e:
            print(f"Error setting replay gain mode: {e}")
            self.error_message = str(e)
            return False

    async def shuffle(self):
        try:
            await self.connect()
            await self.client.shuffle()
            return True
        except Exception as e:
            print(f"Error in shuffle: {e}")
            self.error_message = str(e)
            return False
