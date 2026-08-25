'''Module for application constants.'''
import os
import platform

from dotenv import load_dotenv

def __loadenv__() -> bool:
    return load_dotenv()

def __discogsurl__():
    return os.getenv("DISCOGS_URL")

def __dicogsusertoken__():
    return os.getenv("DISCOGS_USER_TOKEN")

def __lasftfmurl__():
    return os.getenv("LASTFM_URL")

def __lastfmkey__():
    return os.getenv("LASTFM_KEY")

def __musicbrainzurl__():
    return os.getenv("MUSIC_BRAINZ_URL")

def __debugflg__() -> bool:
    if os.getenv("DEBUG") == 'True':
        return True
    return False

def __yes__() -> str:
    '''y'''
    return "y"

def __no__() -> str:
    '''n'''
    return "n"

def __tmpdir__() -> str:
    '''ALBUM'''
    return "ALBUM"

def __mp3__() -> str:
    return "mp3"

def __lastfm__() -> str:
    '''LASTFM'''
    return "LASTFM"

def __discogs__() -> str:
    '''DISCOGS'''
    return "DISCOGS"

def __retry__() -> str:
    '''RETRY'''
    return "RETRY"

def __manualsearch__() -> str:
    '''MANUAL_SEARCH'''
    return "MANUAL_SEARCH"

def __manualentry__() -> str:
    '''MANUAL_ENTRY'''
    return "MANUAL_ENTRY"

def __project_root__() -> str:
    return os.path.dirname(os.path.abspath(__file__)).split("src")[0]

def __disk_path__() -> str:
#    if platform.system() == "linux":
#        return os.getenv("DISK_LINUX")

#    if platform.system() == "Darwin":
#        return os.getenv("DISK_LINUX")

#    return os.getenv("DISK_WINDOWS")
    return os.getenv("DISK_LINUX")
