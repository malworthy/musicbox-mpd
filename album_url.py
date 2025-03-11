import sqlite3
import urllib.parse
import json
import sys
import argparse

# This script will generate an auto play url for all albums in collection.


parser = argparse.ArgumentParser()
parser.add_argument('server')
parser.add_argument('--artist', action="store_true",
                    help="include artist")
parser.add_argument('--album', action="store_true", help="include album")

args = parser.parse_args()
print(args)

con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()

f = open("config.json")
config = json.load(f)
f.close()

cur.execute(
    "select distinct album from library order by albumartist, album")
rows = cur.fetchall()

for row in rows:
    album = urllib.parse.quote(row[0])
    columns = []
    if args.artist:
        a = cur.execute(
            "select albumartist from library where album = ?", (row[0],))
        artist_row = a.fetchone()
        columns.append(artist_row[0])
    if args.album:
        columns.append(row[0])
    columns.append(f"http://{args.server}:{config['port']}/autoplay/{album}")
    print(",".join(columns))
