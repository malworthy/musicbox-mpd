from mpd import MPDClient
import os


class MusicPlayer:

    def __init__(self, host="localhost", port=6600):
        self.host = host
        self.port = port
        self.client = self.create_client()

    """ Check if the client is connected to the server, if not, connect """

    def connect(self):
        try:
            self.client.ping()
        except Exception as e:
            print(f"Reconnecting to server: {e}")
            self.client.connect(self.host, self.port)

    def create_client(self):
        client = MPDClient()
        client.timeout = 10
        client.idletimeout = None
        client.connect("musicbox", 6600)
        return client

    def cache_library(self, con):
        self.connect()
        print(self.client.mpd_version)
        songs = self.client.search("any", "")
        result = [(x.get("file"), x.get("title"), x.get("artist"), x.get("album"), x.get(
            "albumartist"), x.get("track"), x.get("time"), x.get("date")) for x in songs]
        # client.disconnect()
        try:
            con.execute("create table library(id INTEGER PRIMARY KEY, filename text, tracktitle text, artist text, album text, albumartist text, tracknumber int, length int, year text)")
        except:
            print("Library table already exists")
        con.executemany(
            "insert into library(filename,tracktitle,artist, album, albumartist, tracknumber, length, year) values (?,?,?,?,?,?,?,?)", result)
        print("Library cached")

    def add_to_queue(self, uri):
        try:
            self.connect()
            self.client.add(uri)
        except Exception as e:
            print(f"Error adding song to queue: {e}")
            return False
        return True

    def remove_from_queue(self, id):
        try:
            self.connect()
            self.client.deleteid(id)
        except Exception as e:
            print(f"Error removing song from queue: {e}")
            return False
        return True

    def clear_queue(self):
        try:
            self.connect()
            self.client.clear()
        except Exception as e:
            print(f"Error clearing queue: {e}")
            return False
        return True

    def get_queue(self):
        try:
            self.connect()
            queue = self.client.playlistinfo()
        except Exception as e:
            print(f"Error getting queue: {e}")
            return []
        return queue

    def clear_queue(self):
        try:
            self.connect()
            self.client.clear()
        except Exception as e:
            print(f"Error clearing queue: {e}")
            return False
        return True

    def play(self):
        try:
            self.connect()
            self.client.play(0)
        except Exception as e:
            print(f"Error playing song: {e}")
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
            result = dict(volume=s.get("volume"), state=s.get("state"), songid=s.get(
                "songid"), elapsed=s.get("elapsed"), duration=s.get("duration"))
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
            folder = os.path.dirname(uri)
            folder = folder.replace("/", "-").replace("\\", "-")
            filename = "_" + "".join(
                x for x in folder if x.isalnum() or x == "-") + ".jpg"
            filename = os.path.join(img_folder, filename)
            if os.path.exists(filename):
                return filename

            self.connect()
            img = self.client.albumart(uri)
            with open(filename, "wb") as file:
                file.write(img["binary"])
            return filename
        except Exception as e:
            print(f"Error getting cover art: {e}")
            return None

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
