import os
import subprocess

import core.utility as util

from src.globalconstants import __disk_path__
from core.odno_cache import odno_cache
from collections import deque

from core.odnoexceptions import OdnoException


DISK = __disk_path__()

def rip():
    '''rip tracks from disk using ffmpeg'''
    try: 
        mpath = os.path.expanduser("~") + "/Music"

        if os.path.isdir(mpath):
            odno_cache["mpath"] = mpath

        album = util.clean_input_str("\nenter album name: ")
        artist = util.clean_input_str("enter artist name: ")

        album = album.replace(" ", "_")
        artist = artist.replace(" ", "_")

        odno_cache['album'] = album
        odno_cache['artist'] = artist

        album_dir = f"{mpath}/{album}-{artist}"
        if os.path.isdir(album_dir):
            subprocess.run(f"rm -rf {album_dir}", shell=True, check=True)

        os.mkdir(album_dir)
        odno_cache["album_dir"] = album_dir

        disk = os.path.abspath(DISK)
        if os.path.isdir(disk):
            odno_cache['disk'] = disk

        dir_list = os.listdir(disk)
        
        odno_cache['unsorted_dir_list'] = dir_list

        dir_list = deque(dir_list)

        print("Starting disc rip. This may take awhile...")
        for track in dir_list:
            track_file = track.replace(" ", "").replace(".",".odno.").lower()
            dest = f"{album_dir}/{track_file}"

            print(f"ripping {track} from disc to {dest}")

            rip_cmd = f"ffmpeg -i {disk}/'{track}' -vn -c:a copy {dest}"
            subprocess.run([rip_cmd], shell=True, check=True)

        print("\nripping complete!")
        print(f"tracks stored in {album_dir}")
    except (TypeError, subprocess.CalledProcessError) as e:
        print("Rip failed. Make sure disk path is correct and there are valid audio files on disk.")
        oe = OdnoException("Rip Failed", e)
        raise oe from e


# TODO: delet this soon.
if __name__ == "__main__":
    rip()
