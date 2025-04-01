from mpd import MPDClient
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

    def connect(self):
        if self.client == None:
            self.client = self.create_client()
            self.client.connect(self.host, self.port)
            return

        try:
            self.client.ping()
        except mpd.ConnectionError as e:
            print(f"Reconnecting to server: {e}")
            self.client.connect(self.host, self.port)
        except Exception as e:
            print(f"Exception occurred connecting: {e}")

    def create_client(self):
        client = MPDClient()
        client.timeout = 10
        client.idletimeout = None
        return client

    def cache_library(self, con):
        self.connect()
        print(self.client.mpd_version)
        songs = self.client.search("any", "")
        result = [(x.get("file"), x.get("title"), x.get("artist"), x.get("album"), x.get(
            "albumartist"), x.get("track"), x.get("time"), x.get("date")) for x in songs]
        con.execute("delete from library")
        con.executemany(
            "insert into library(filename,tracktitle,artist, album, albumartist, tracknumber, length, year) values (?,?,?,?,?,?,?,?)", result)
        print("Library cached")

    def get_mpd_version(self):
        try:
            self.connect()
            return self.client.mpd_version
        except Exception as e:
            print(f"Error getting MPD version: {e}")
            self.error_message = str(e)
            return "Error getting MPD version"

    def add_to_queue(self, uri):
        try:
            self.connect()
            self.client.add(uri)
        except Exception as e:
            print(f"Error adding song to queue: {e}")
            self.error_message = str(e)
            return False
        return True

    def remove_from_queue(self, id):
        try:
            self.connect()
            self.client.deleteid(id)
        except Exception as e:
            print(f"Error removing song from queue: {e}")
            self.error_message = str(e)
            return False
        return True

    def clear_queue(self):
        try:
            self.connect()
            self.client.clear()
        except Exception as e:
            print(f"Error clearing queue: {e}")
            self.error_message = str(e)
            return False
        return True

    def get_queue(self):
        try:
            self.connect()
            queue = self.client.playlistinfo()
        except Exception as e:
            print(f"Error getting queue: {e}")
            self.error_message = str(e)
            return []
        return queue

    def clear_queue(self):
        try:
            self.connect()
            self.client.clear()
        except Exception as e:
            print(f"Error clearing queue: {e}")
            self.error_message = str(e)
            return False
        return True

    def play(self):
        try:
            self.connect()
            self.client.play(0)
        except Exception as e:
            print(f"Error playing song: {e}")
            self.error_message = str(e)
            return False
        return True

    def stop(self):
        try:
            self.connect()
            self.client.stop()
        except Exception as e:
            print(f"Error stopping song: {e}")
            return False
        return True

    def status(self):
        try:
            self.connect()
            s = self.client.status()
            songid = s.get("songid")
            # result = dict(volume=s.get("volume"), state=s.get("state"), songid=s.get(
            #     "songid"), elapsed=s.get("elapsed"), duration=s.get("duration"), song=s.get("song"),
            #     audio=s.get("audio"), updating_db=s.get("updating_db"), playlistlength=s.get("playlistlength"))
            result = s
            if songid != None:
                d = self.client.playlistid(songid)

                if len(d) > 0:
                    result["title"] = d[0].get("title")
                    result["artist"] = d[0].get("artist")
                    result["file"] = d[0].get("file")
            return result
        except Exception as e:
            print(f"Error getting status: {e}")
            return {}

    def pause(self):
        try:
            print("in pause")
            self.connect()
            s = self.client.status()
            state = s.get("state")
            if state == "pause":
                self.client.pause(0)
            else:
                self.client.pause(1)
        except Exception as e:
            print(f"Error pausing song: {e}")
            return False
        return True

    def volume(self, vol):
        try:
            self.connect()
            self.client.volume(vol)
            s = self.client.status()
            return s.get("volume")
        except Exception as e:
            print(f"Error setting volume: {e}")
            return "Cannot set volume"

    def get_cover_art(self, uri, img_folder):
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

            self.connect()
            img = self.client.readpicture(uri)
            if img.get("binary") == None:
                print("embedded art not found - looking up albumart")
                img = self.client.albumart(uri)

            with open(filename, "wb") as file:
                file.write(img["binary"])
            return filename
        except Exception as e:
            print(f"Error getting cover art: {e}")
            return None

    # def get_cover_art(self, uri, img_folder):
    #     if img_folder == None:
    #         return None
    #     try:
    #         if os.path.exists(img_folder) == False:
    #             os.makedirs(img_folder)
    #     except Exception as e:
    #         print(f"Error creating folder: {e}")
    #         return None

    #     try:
    #         folder = os.path.dirname(uri)
    #         folder = folder.replace("/", "-").replace("\\", "-")
    #         filename = "_" + "".join(
    #             x for x in folder if x.isalnum() or x == "-") + ".jpg"
    #         filename = os.path.join(img_folder, filename)
    #         if os.path.exists(filename):
    #             return filename

    #         print(f"getting image {time.strftime('%X')}")
    #         local_client = self.create_client()
    #         local_client.connect(self.host, self.port)
    #         # self.connect()
    #         img = local_client.albumart(uri)
    #         local_client.disconnect()

    #         print(f"got image from MPD {time.strftime('%X')}")
    #         with open(filename, "wb") as file:
    #             file.write(img["binary"])
    #         print(f"Saved image to disk {time.strftime('%X')}")
    #         return filename
    #     except Exception as e:
    #         print(f"Error getting cover art: {e}")
    #         return None

    def skip(self):
        try:
            self.connect()
            self.client.next()
        except Exception as e:
            print(f"Error skipping song: {e}")
            return False
        return True

    def save_playlist(self, name):
        try:
            self.connect()
            self.client.save(name)
        except Exception as e:
            print(f"Error saving playlist: {e}")
            self.error_message = str(e)
            return False
        return True

    def update_playlist(self, name):
        try:
            self.connect()
            self.client.rm(name)
            self.client.save(name)
        except Exception as e:
            print(f"Error updating playlist: {e}")
            return False
        return True

    def delete_playlist(self, name):
        try:
            self.connect()
            self.client.rm(name)
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False
        return True

    def get_playlists(self):
        try:
            self.connect()
            playlists = self.client.listplaylists()
        except Exception as e:
            print(f"Error getting playlists: {e}")
            return []
        return playlists

    def load_playlist(self, name):
        try:
            self.connect()
            self.client.load(name)
        except Exception as e:
            print(f"Error loading playlist: {e}")
            return False
        return True

    def update(self, con):
        try:
            self.connect()
            status = self.client.status()
            updating = status.get("updating_db")
            if updating != None:
                return updating

            result = self.client.update()
            thread = Thread(target=self.wait_for_update, args=(con, ))
            thread.start()
        except Exception as e:
            print(f"Error updating library: {e}")
            return None
        return result

    def wait_for_update(self, con):
        try:
            local_client = self.create_client()
            local_client.connect(self.host, self.port)
            for i in range(2):
                # self.connect()
                print("Waiting for update")
                local_client.idle("update")
                print("update event happened")
                status = local_client.status()
                updating = status.get("updating_db")
                print(f"Updating: {updating}")
                if updating == None:
                    self.cache_library(con)
                    return True
        except Exception as e:
            print(f"Error waiting for update: {e}")
            return False
        finally:
            local_client.close()
        return False

    def set_setting(self, name, value):
        try:
            self.connect()
            if name == "random":
                self.client.random(value)
            elif name == "repeat":
                self.client.repeat(value)
            elif name == "consume":
                self.client.consume(value)
        except Exception as e:
            print(f"Error setting value: {e}")
            return False

    def get_replay_gain_status(self):
        try:
            self.connect()
            return self.client.replay_gain_status()
        except Exception as e:
            print(f"Error getting replay gain status: {e}")
            self.error_message = str(e)
            return None

    def set_replay_gain_mode(self, mode):
        try:
            self.connect()
            self.client.replay_gain_mode(mode)
            return True
        except Exception as e:
            print(f"Error setting replay gain mode: {e}")
            self.error_message = str(e)
            return False

    def shuffle(self):
        try:
            self.connect()
            self.client.shuffle()
            return True
        except Exception as e:
            print(f"Error in shuffle: {e}")
            self.error_message = str(e)
            return False
