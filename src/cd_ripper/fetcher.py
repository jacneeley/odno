import requests
import sys

from bs4 import BeautifulSoup

import discogs_client
from scripts.globals import load_env, DISCOGS_URL, DISCOGS_USER_TOKEN, LASTFM_KEY, LASTFM_URL, MUSIC_BRAINZ_URL
from src.utility import convert_date_str

if not load_env():
    print("failed to load env vars...")
    sys.exit()


def auth_user() -> discogs_client.Client:
    '''
        Return Client object from discogs using a user_token
    '''
    d = discogs_client.Client("cdripper/0.1", user_token=DISCOGS_USER_TOKEN())
    return d

def get_album_discogs(query:str) -> dict:
    '''
        Use discog's authorized client to search its api for an album via its "master_id".

        parameters:
            * query -> search query following: 'album name by artist' i.e. 'daydream nation by sonic youth'

        returns:
            * JSON response.
    '''

    master_id = auth_user().search(query=query, type="release")[0].data['master_id']

    resp:requests.Response = requests.get(DISCOGS_URL() + str(master_id), timeout=20)
    return resp.json()

def get_album_lastfm(artist:str, album:str, debug:bool) -> dict:
    '''
        Search lastfm for album data using album name and artist name.

        parameters:
            * artist -> name of the artist string
            * album -> name of the album string
            * debug -> show debug info in console bool

        returns:
            * JSON response.
    '''
    api_key = f"&api_key={LASTFM_KEY()}"
    artist_str = f"&artist={artist}"
    album_str = f"&album={album}"
    format_str = "&format=json"
    query = LASTFM_URL() + api_key + artist_str + album_str + format_str

    if debug:
        print("searching using:",query)

    resp:requests.Response = requests.get(query, timeout=20)
    
    if debug:
        print("lastfm response:\n", resp.content)

    if resp.ok:
        return resp.json()
    
    print("could not get find:",query,"\nresponse status:",resp.status_code)
    print(resp.raise_for_status())
    return {}

def fetch_date_from_music_brainz(mbid:str , debug:bool) -> str:
    '''
        You would think lastfm would return the release date in their api response but they don't.
        To get around that, this method will grab the mbid and use it to search for the album release date on MusicBrainz.

        parameters:
            * mbid -> MusicBrainz ID string
            * debug -> show debug info in console bool
        
        returns:
            * original release date of the album as a string.
    '''


    query = MUSIC_BRAINZ_URL().replace("MBID", mbid)
    
    resp = requests.get(query, timeout=20)

    if debug:
        print("searching for:",query)
        print("response:\n",resp)

    if resp.ok:
        soup = BeautifulSoup(resp.text, features="xml")
        return convert_date_str(soup.find("first-release-date").string)
    
    print("Could not get datetime from musicbrainz...\n", "response code:", resp.status_code)
    return "N/A"

if __name__ == "__main__":
    print("testing connection with supplied client_id & client_secret...")
    test = auth_user().search("Daydream Nation by Sonic Youth", type="release")
    results = test[0].data
    print(results)

    print(get_album_discogs("daydream nation by sonic youth"))
    print(get_album_lastfm("sonic+youth", "goo", True))

    test = fetch_date_from_music_brainz("18eb7b48-83a5-49d8-b8a0-04ee2b123b2d", True)
    print(test)