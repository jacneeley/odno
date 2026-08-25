'''CD RIPPER'''
import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

import core.utility as util

from src.global_constants import __disk_path__
from core.odno_cache import odno_cache

from exceptions.odno_exceptions import OdnoException

def __process_tracks(dir_list, disk, album_dir):
    try:
        for track in dir_list:
            track_file = track.replace(" ", "").replace(".",".odno.").lower()
            dest = f"{album_dir}/{track_file}"

            print(f"ripping {track} from disc to {dest}")

            rip_cmd = f"ffmpeg -i {disk}/'{track}' -vn -c:a copy {dest}"
            process = subprocess.run([rip_cmd], shell=True, check=True)
            if process.returncode != 0:
                print(f"rip failed: {process.stderr}...skipping...")
                continue
            
    except (TypeError, subprocess.CalledProcessError) as e:
        print("Rip failed. Make sure disk path is correct and there are valid audio files on disk.")
        oe = OdnoException("Rip Failed", e)
        raise oe from e

def rip():
    '''rip tracks from disk using ffmpeg'''
    DISK = __disk_path__()
    mpath = odno_cache.get("MUSIC_PATH", os.path.expanduser("~") + "/Music")

    if os.path.isdir(mpath):
        odno_cache["mpath"] = mpath

    album = util.clean_input_str("\nenter album name: ")
    artist = util.clean_input_str("enter artist name: ")

    album = album.replace(" ", "_")
    artist = artist.replace(" ", "_")

    odno_cache['album_name'] = album
    odno_cache['artist_name'] = artist

    try:
        album_dir = f"{mpath}/{album}-{artist}"
        if os.path.isdir(album_dir):
            subprocess.run(f"rm -rf {album_dir}", shell=True, check=True)
    except subprocess.CalledProcessError as cpe:
        print("Error: Directory issue...")
        OdnoException.handle_exception(OdnoException(f"{album_dir} could not be removed for some reason.", cpe), cpe.stderr, "rip.rip")

    os.mkdir(album_dir)
    odno_cache["album_dir"] = album_dir

    disk = os.path.abspath(DISK)
    if not os.path.isdir(disk):
        print("No disc or CDROM drive found...")
        sys.exit()

    odno_cache['disk'] = disk

    dir_list = os.listdir(disk)

    odno_cache['unsorted_dir_list'] = dir_list

    mid = int((len(dir_list) - 1) / 2)
    print("Starting disc rip. This may take awhile...")
    # __process_tracks(dir_list, disk, album_dir)

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(__process_tracks, dir_list[:mid], disk, album_dir)
            executor.submit(__process_tracks, dir_list[mid:], disk, album_dir)

    except (OdnoException, Exception) as e:
        OdnoException.handle_exception(e)
        print("Exiting to prevent issues")
        executor.shutdown()
        sys.exit()

    executor.shutdown(wait=True)

    print("\nripping complete!")
    print(f"tracks stored in {album_dir}")
