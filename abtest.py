from pygame import mixer
import pygame
import time
import glob
import random
import argparse
import os


def play(filename):
    mixer.music.load(filename)
    # print(f"Playing song {filename}")
    mixer.music.play()
    time.sleep(30)
    mixer.music.stop()


pygame.init()
mixer.init()

parser = argparse.ArgumentParser()
parser.add_argument('path')

args = parser.parse_args()

file_path = "c:/tmp/"

files = glob.glob(os.path.join(file_path, "*.mp3"))
files.extend(glob.glob(os.path.join(file_path, "*.flac")))

random.shuffle(files)

print("Playing 2 audio files, can you tell which one is high quality?")
count = 1
for file in files:
    print(f"Playing file {count}")
    play(file)
    count += 1
input("Which one was the highest quality: ")
count = 1
for file in files:
    print(f"File {count} was {file}")
    count += 1
print("You didn't get it did you - and if you did it was just luck")
