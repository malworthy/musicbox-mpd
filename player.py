from data import create_connection, get_next_song, is_paused, setplaying
from pygame import mixer
import pygame
import time


def playasync(row):
    con2 = create_connection()

    filename = row['filename']
    id = row['id']
    mixer.music.load(row['filename'])
    print(f"Playing song {filename}")
    mixer.music.play()
    mixer.music.set_endevent(1)

    songs_in_queue = True
    while songs_in_queue:

        row = get_next_song(con2)
        if row != None:
            mixer.music.queue(row['filename'])
        else:
            print("no more songs in queue")
            songs_in_queue = False

        wait = True
        while wait:
            print(" -- in wait loop --")
            time.sleep(0.1)
            if not mixer.music.get_busy() and is_paused(con2) == False:
                wait = False
                songs_in_queue = False
                print("stop pressed")
            for event in pygame.event.get():
                if event.type == 1:
                    wait = False

        print(f"finished playing song {filename} and deleting from queue")
        con2.execute("delete from queue where playing is not null")
        con2.commit()

        if songs_in_queue == False:
            row = get_next_song(con2)
            if row != None:
                print(
                    "a song was added to the queue after the last song started playing")
                mixer.music.load(row['filename'])
                mixer.music.play()
                mixer.music.set_endevent(1)
                songs_in_queue = True
            else:
                print("at the end of the queue - exiting play loop")
                return

        filename = row['filename']
        id = row['id']
        setplaying(id, con2)
