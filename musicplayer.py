from mpd import MPDClient


class MusicPlayer:

    def __init__(self):
        self.client = self.create_client()

    """ Check if the client is connected to the server, if not, connect """

    def connect(self):
        try:
            self.client.ping()
        except Exception as e:
            print(f"Reconnecting to server: {e}")
            self.client.connect("musicbox", 6600)

    def create_client(self):
        client = MPDClient()
        client.timeout = 10
        client.idletimeout = None
        client.connect("musicbox", 6600)
        return client

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

    def get_cover_art(self, uri):
        try:
            filename = "c:\\tmp\\cover.jpg"
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

    # def add_album(self, uri):
    #     try:
    #         self.connect()
    #         self.client.findadd("album", uri)
    #     except Exception as e:
    #         print(f"Error adding album to queue: {e}")
    #         return False
    #     return True
