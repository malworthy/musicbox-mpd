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
            self.client.next()
        except Exception as e:
            print(f"Error playing song: {e}")
            return False
        return True
