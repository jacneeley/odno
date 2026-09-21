'''Module for making requests to APIs.'''
import sys
from bs4 import BeautifulSoup

import discogs_client
import src.global_constants as global_constants
from core.odno_logging import odnologger

from core.utility import convert_date_str
from models.models import ResponseBodyBuilder, ResponseBody

MODULE_NAME = "fetcher"

if not global_constants.__loadenv__():
    print("failed to load env vars...")
    sys.exit()


def auth_user() -> discogs_client.Client:
    '''
        Return Client object from discogs using a user_token
    '''
    d = discogs_client.Client("cdripper/0.1", user_token=global_constants.__dicogsusertoken__())
    return d

def get_album_discogs(query:str) -> ResponseBody:
    '''
        Use discog's authorized client to search its api for an album via its "master_id".

        parameters:
            * query -> search query following: 'album name by artist' i.e. 'daydream nation by sonic youth'

        returns:
            * JSON response.
    '''

    master_id = auth_user().search(query=query, type="release")[0].data['master_id']
    url = global_constants.__discogsurl__() + str(master_id)

    response_body:ResponseBody = (ResponseBodyBuilder()
                                  .url(url)
                                  .debug(global_constants.__debugflg__())
                                  .build())
    
    return response_body.get()

def get_album_lastfm(artist:str, album:str) -> ResponseBody:
    '''
        Search lastfm for album data using album name and artist name.

        parameters:
            * artist -> name of the artist string
            * album -> name of the album string
            * debug -> show debug info in console bool

        returns:
            * JSON response.
    '''
    api_key = f"&api_key={global_constants.__lastfmkey__()}"
    artist_str = f"&artist={artist}"
    album_str = f"&album={album}"
    auto_correct = "&autocorrect=1"
    format_str = "&format=json"
    query = global_constants.__lasftfmurl__() + api_key + artist_str + album_str + auto_correct + format_str

    response_body:ResponseBody = (ResponseBodyBuilder()
                                  .url(query)
                                  .debug(global_constants.__debugflg__())
                                  .build())

    if response_body.debug:
        odnologger.log(log_level="INFO", msg=f"searching using: {query}", module_name=f"{MODULE_NAME}.get_album_lastfm")

    # if response_body.debug and response_body.response:
    #     print("lastfm response:\n", response_body.response)

    return response_body.get()

def fetch_date_from_music_brainz(mbid:str) -> str:
    '''
        You would think lastfm would return the release date in their api response but they don't.
        To get around that, this method will grab the mbid and use it to search for the album release date on MusicBrainz.

        parameters:
            * mbid -> MusicBrainz ID string
            * debug -> show debug info in console bool
        
        returns:
            * original release date of the album as a string.
    '''


    query = global_constants.__musicbrainzurl__().replace("MBID", mbid)

    response_body = (ResponseBodyBuilder()
                     .url(query)
                     .debug(global_constants.__debugflg__())
                     .build())

    response_body.get()



    if not response_body.is_success:
        print("Release Date could not be found...")
        odnologger.log(log_level="INFO", msg=f"Could not get datetime from musicbrainz...\nresponse code: {response_body.response_code}"
                       , module_name=f'{MODULE_NAME}.fetch_date_from_music_brainz')
        return "N/A"

    elif response_body.debug:
        odnologger.log(log_level="INFO", msg=f"searching for: {query}",
                         module_name=f'{MODULE_NAME}.fetch_date_from_music_brainz')
        odnologger.log(log_level="INFO", msg=f"response:{response_body.response.text}",
                         module_name=f'{MODULE_NAME}.fetch_date_from_music_brainz')

    soup = BeautifulSoup(response_body.response.text, features="xml")
    target = soup.find("first-release-date").string
    if not target:
        print("Could not get datetime from musicbrainz...")
        return "N/A"

    return convert_date_str(soup.find("first-release-date").string)
