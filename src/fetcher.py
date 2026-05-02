'''Module for making requests to APIs.'''
import sys
from bs4 import BeautifulSoup

import discogs_client
import core.globalconstants as globalconstants
import core.odnologging as odnologging

from core.utility import convert_date_str
from src.models import ResponseBodyBuilder, ResponseBody

logger = odnologging.create_logger("fetcher.py")

if not globalconstants.__loadenv__():
    print("failed to load env vars...")
    sys.exit()


def auth_user() -> discogs_client.Client:
    '''
        Return Client object from discogs using a user_token
    '''
    d = discogs_client.Client("cdripper/0.1", user_token=globalconstants.__dicogsusertoken__())
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
    url = globalconstants.__discogsurl__() + str(master_id)

    response_body:ResponseBody = (ResponseBodyBuilder()
                                  .url(url)
                                  .debug(globalconstants.__debugflg__())
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
    api_key = f"&api_key={globalconstants.__lastfmkey__()}"
    artist_str = f"&artist={artist}"
    album_str = f"&album={album}"
    format_str = "&format=json"
    query = globalconstants.__lasftfmurl__() + api_key + artist_str + album_str + format_str

    response_body:ResponseBody = (ResponseBodyBuilder()
                                  .url(query)
                                  .debug(globalconstants.__debugflg__())
                                  .build())
    
    if response_body.debug:
        logger.info("searching using: %s", query, exc_info=1)

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


    query = globalconstants.__musicbrainzurl__().replace("MBID", mbid)
    
    # resp = requests.get(query, timeout=20)
    response_body = (ResponseBodyBuilder()
                     .url(query)
                     .debug(globalconstants.__debugflg__())
                     .build())

    response_body.get()

    if response_body.debug:
        logger.info("searching for: %s",query)
        logger.info("response:\n%s",response_body.response.text)

    if not response_body.is_success:
        logger.info("Could not get datetime from musicbrainz...\nresponse code: %s", response_body.response_code)
        return "N/A"
    
    soup = BeautifulSoup(response_body.response.text, features="xml")
    target = soup.find("first-release-date").string
    if not target:
        logger.info("Could not get datetime from musicbrainz...")
        return "N/A"

    return convert_date_str(soup.find("first-release-date").string)


if __name__ == "__main__":
    print("testing connection with supplied client_id & client_secret...")
    test = auth_user().search("Daydream Nation by Sonic Youth", type="release")
    results = test[0].data
    print(results)

    print(get_album_discogs("daydream nation by sonic youth"))
    print(get_album_lastfm("sonic+youth", "goo"))

    test = fetch_date_from_music_brainz("18eb7b48-83a5-49d8-b8a0-04ee2b123b2d")
    print(test)