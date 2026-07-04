import os
import subprocess

from collections import deque

DISC = "/run/user/1000/gvfs/cdda:host=sr0"
CMD:str = "ffmpeg -i \"<t>\" -vn -c:a copy <dest>"

def rip():
    '''rip tracks from disk using ffmpeg'''
    mpath = os.path.expanduser("~") + "/Music/odno_testing"

    album = input("enter album name: ")
    artist = input("enter artist name: ")

    album = album.replace(" ", "_")
    artist = artist.replace(" ", "_")

    #TODO: maybe cache this?
    album_dir = f"{mpath}/{album}-{artist}"
    if os.path.isdir(album_dir):
        subprocess.call(f"rm -rf f{album_dir}")

    os.mkdir(album_dir)

    disc = os.path.abspath(DISC)

    dir_list = os.listdir(disc)
    dir_list = deque(dir_list)

    print("Starting disc rip. This may take awhile...")
    for track in dir_list:
        track_file = track.replace(" ", "").replace(".",".odno.").lower()
        dest = f"{album_dir}/{track_file}"

        print(f"ripping {track} from disc to {dest}")

        rip_cmd = f"ffmpeg -i {disc}/'{track}' -vn -c:a copy {dest}"
        subprocess.run([rip_cmd], shell=True, check=False)

    print("\nripping complete!")
    print(f"tracks stored in {album_dir}")

if __name__ == "__main__":
    rip()
