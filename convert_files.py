import glob
import json
import sys
import os
import subprocess

def get_files(ext):
    print("Retreiving files")

    return glob.glob(f"{config['library']}**/*.{ext}", recursive=True)

def convert_files(ext):
    default_ext = config["extensions"][0]
    print("converting files")

    for file in get_files(ext):
        print(file)
        outfile = file.replace(".m4a",".mp3")
        if not os.path.isfile(outfile):
            cmd = f"ffmpeg -i \"{file}\" -ab `ffmpeg -i \"{file}\" 2>&1 | grep Audio | awk -F', ' '{{print $5}}' | cut -d' ' -f1`k -map_metadata 0 -id3v2_version 3 -write_id3v1 1 \"{outfile}\""
            print(cmd)
            subprocess.call(cmd, shell=True)

## main entry point ##

f = open("config.json")
config = json.load(f)
f.close()

convert_files("m4a")

print("finished")