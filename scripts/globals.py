import os

from dotenv import load_dotenv

def load_env() -> bool:
    return load_dotenv()

def DISCOGS_URL():
    return os.getenv("DISCOGS_URL")

def DISCOGS_USER_TOKEN():
    return os.getenv("DISCOGS_USER_TOKEN")

def LASTFM_URL():
    return os.getenv("LASTFM_URL")

def LASTFM_KEY():
    return os.getenv("LASTFM_KEY")

def MUSIC_BRAINZ_URL():
    return os.getenv("MUSIC_BRAINZ_URL")
