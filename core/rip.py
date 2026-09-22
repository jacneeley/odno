'''CD RIPPER'''
import os
import sys
import subprocess
import wave

from concurrent.futures import ThreadPoolExecutor, Future

import cdio
import pycdio

from tqdm import tqdm

import core.utility as util

from models.odno_cache import odno_cache
from core.odno_logging import logger
from exceptions.odno_exceptions import OdnoException

__track_map = {}
__cache = odno_cache.get_cache()
odnologger = logger()

def init_device() -> None:
    '''set up cdrom drive'''
    try:
        d = cdio.Device(driver_id=pycdio.DRIVER_UNKNOWN)
        drive_name = d.get_device()

        if "GNU/Linux" in cdio.drivers:
            __cache['drive'] = cdio.Device(driver_id=pycdio.DRIVER_LINUX)
        else:
            __cache['drive'] = d

        __cache['disk'] = drive_name

        return drive_name

    except (OSError, cdio.NoDriverError, cdio.DeviceException) as e:
        msg = "No drive found..."
        odnologger.log(log_level="ERROR", msg=msg, e=e, module_name="rip.init_device")
        print(msg)

def __process_tracks(track:str, raw_audio:bytes):
    try:
        album_dir = __cache.get("album_dir", __cache["MUSIC_PATH"])

        with wave.open(f"{album_dir}/{track}.wav", "wb") as w:
            w.setnchannels(2) #pylint: disable=no-member
            w.setsampwidth(2) #pylint: disable=no-member
            w.setframerate(44100) #pylint: disable=no-member
            w.writeframes(raw_audio) #pylint: disable=no-member

    except Exception as e:
        print("Rip failed. Make sure disk path is correct and there are valid audio files on disk.")
        ioe = IOError(f"Rip failed on {track}", e)
        raise ioe from e

def __rip_tracks_off_disc(track_num:int, track:cdio.Track, d:cdio.Device) -> None:
    """
    read data per track.
    
    parameters:
        * num -> the track num (int)
        * track -> cdio.Track
        * d -> CDROM (cdio.Device)

    Note:
        To calculate the block size using the Logical Sector Number (LSN) from a CD-ROM,
        you typically need to know the total size of the CD and the number of sectors it contains.
        The block size is usually determined by dividing the total size of the CD (in bytes) by the number of sectors.
        For standard CDs, the block size is often 2048 bytes per sector.
    """
    try:
        # test = track.get_cdtext()
        # track:cdio.Track = d.get_track(track_num)
        if track.get_format() == "audio":
            lsn = track.get_lsn()
            last_lsn = track.get_last_lsn()

            audio_chunks = []
            while lsn <= last_lsn:
                sector = d.read_sectors(lsn, pycdio.READ_MODE_AUDIO)
                audio_chunks.append(sector[1])
                lsn += 1

            audio_bytes = b''.join(a.encode('utf-8', errors="surrogateescape") for a in audio_chunks)
            __track_map[f"{track_num}_track"] = audio_bytes

        else:
            print("invalid. Did you insert a CD?")
            msg = "CDROM contents were not audio files"
            raise IOError(msg)

    except (IOError, cdio.DeviceException, TypeError, Exception) as e:
        msg = "failed to rip CD"
        print(msg)
        d.close()
        raise OdnoException(message=msg, e=e) from e

def rip() -> bool:
    '''rip tracks from disk using ffmpeg'''
    # DISK = __disk_path__()
    drive:cdio.Device = None
    __track_map.clear()

    try:
        drive = __cache.get('drive', cdio.Device(driver_id=pycdio.DRIVER_UNKNOWN))

    except (KeyError, IOError) as e:
        oe = OdnoException("CD-ROM cannot be accessed.", e)
        print(oe.message)
        OdnoException.handle_exception(oe, oe.message, "rip.rip")
        return False

    mpath = __cache.get("MUSIC_PATH", os.path.expanduser("~") + "/Music")

    if os.path.isdir(mpath):
        __cache["MUSIC_PATH"] = mpath

    album = util.clean_input_str("\nenter album name: ")
    artist = util.clean_input_str("enter artist name: ")

    album = album.replace(" ", "_")
    artist = artist.replace(" ", "_")

    __cache['album_name'] = album
    __cache['artist_name'] = artist

    try:
        album_dir = f"{mpath}/{album}-{artist}"
        if os.path.isdir(album_dir):
            subprocess.run(f"rm -rf {album_dir}", shell=True, check=True)
    except subprocess.CalledProcessError as cpe:
        print("Error: Directory issue...")
        oe = OdnoException(f"{album_dir} could not be removed for some reason.", cpe)
        raise oe from cpe

    os.mkdir(album_dir)
    __cache["album_dir"] = album_dir

    try:
        t = 1
        total = drive.get_num_tracks()
        print("Starting disc rip. This may take awhile...\n")
        with tqdm(total=total, desc="Ripping Tracks", unit="track") as pbar:
            while t <= total:
                # track_list.append(drive.get_track(t))
                __rip_tracks_off_disc(t, drive.get_track(t), drive)
                pbar.update(1)
                t+=1

    except (OdnoException, cdio.TrackError) as e:
        if not isinstance(e, OdnoException):
            e = OdnoException(e)

        OdnoException.handle_exception(e, e.message, "rip.rip")
        print("exiting to prevent issues")
        drive.close()
        sys.exit(1)

    try:
        # review if needed : https://docs.python.org/3/library/concurrent.futures.html
        with ThreadPoolExecutor(max_workers=len(__track_map) / 2) as executor:
            futures:list[Future] = []
            for track, raw_audio in __track_map.items():
                future = executor.submit(__process_tracks, track, raw_audio)
                futures.append(future)

            for f in tqdm(futures, desc="Writing tracks as WAV files", unit="track"):
                f.result()

    except Exception as e:
        OdnoException.handle_exception(e)
        print("Exiting to prevent issues")
        executor.shutdown()
        # drive.close()
        sys.exit(1)

    executor.shutdown(wait=True)

    print("\nripping complete!")

    print("ejecting...")
    drive.eject_media()

    print(f"tracks stored in {album_dir}")

    return True
