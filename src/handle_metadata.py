'''common module for handling application flow.'''
import os
import requests
import subprocess

from collections import deque

import core.utility as util
import core.prompts as prompts
import core.cmds as cmds
from core.odnologging import odnologger
from core.odnoexceptions import OdnoException
from core.odno_cache import odno_cache

import src.globalconstants as globalconstants
import src.fetcher as fetcher
from src.models import SongBuilder, Song, ResponseBody

MODULE_NAME = "handle_metadata"

#TODO: use cache where applicable

def check_album(album:dict, platform:str) -> dict:
    '''
        Helper function to get album metadata from Spotify.search() and display album, artist, & release date.

        parameters:
            * album -> JSON object from discogs_client.Client(*args).search()
    '''
    tmp = {
        "album" : "",
        "artist": "",
        "release_date": "",
        "source": ""
    }

    try:
        if platform == globalconstants.__lastfm__():
            mbid = album['album']['mbid']
            tmp["album"] = album['album']['name']
            tmp['artist'] = album['album']['artist']
            tmp['release_date'] =  fetcher.fetch_date_from_music_brainz(mbid)
            tmp['source'] = globalconstants.__lastfm__()

        elif platform == globalconstants.__discogs__():
            tmp['album'] = album['title']
            tmp['artist'] = album['artists'][0]['name']
            tmp['release_date'] = util.convert_date_str(album['year'])
            tmp['source'] = globalconstants.__discogs__()

        print("album:",    tmp['album'])
        print("artist:",   tmp['artist'])
        print("release:",  str(tmp['release_date']))

    except KeyError as ke:
        print("Album could not be found...")
        msg = "Album could not be found in lastfm response." if platform == globalconstants.__lastfm__() else "Album could not be found in discogs response."
        oe = OdnoException(msg, ke)
        OdnoException.handle_exception(oe, oe.message, "handle_metadata.check_album")

    odno_cache['album'] = tmp

    return tmp

def get_album_data_from_source(album:dict, resp:dict) -> list[Song]:
    '''retrieve album data from source.'''
    tracks = []

    try:
        odnologger.log(log_level="INFO", msg=f"response: {resp}", module_name=f'{MODULE_NAME}.get_album_data_from_source')
        odnologger.log(log_level="INFO", msg=f"album: {album}", module_name=f'{MODULE_NAME}.get_album_data_from_source')

        album_cover = ""
        genre = ""
        release = "1970-01-01"
        source = album['source']
        track_str = ""

        json_resp = {}

        if source == globalconstants.__discogs__():
            album_cover = resp['images'][0]['uri']
            genre = resp['styles'][0] if len(resp['styles']) > 1 else resp['genres'][0]
            release = album['release_date']
            track_str = 'title'
            json_resp = resp['tracklist']
        
        else:
            if len(resp['album']['image']) > 0:
                album_cover = resp['album']['image'][3]["#text"]

            if resp['album']["tags"] != "":
                genre = resp['album']["tags"]["tag"][0]["name"]

            release = album['release_date']
            track_str = 'name'
            json_resp = resp['album']['tracks']['track']

        track_num = 1
        for t in json_resp:
            song = (SongBuilder()
            .title(t[track_str])
            .artist(album['artist'])
            .album(album['album'])
            .album_artist(album['artist'])
            .genre(genre)
            .year(release)
            .track_num(track_num)
            .cover(album_cover)
            .build())

            track_num += 1
            tracks.append(song)

        odnologger.log(log_level="INFO", msg=f"Tracks: {tracks}", module_name=f'{MODULE_NAME}.get_album_data_from_source')

    except (KeyError, ValueError) as e:
        print("album data could not be retrieved...")

        msg = "KeyError in JSON response" if isinstance(e, KeyError) else "ValueError ocurred building song"

        oe = OdnoException(msg, e)
        OdnoException.handle_exception(oe, oe.message, f"{MODULE_NAME}.get_album_data_from_source")

    return tracks

def valid_discogs_flow(album_query:str) -> list[Song]:
    '''Application will check discogs if lastfm search fails or returns incorrect results.'''
    album_query = album_query.replace("-", " by ").replace("_", " ")
    resp = fetcher.get_album_discogs(album_query)

    if not resp.is_success:
        print("Album data could not be found...")
        resp.show_errors()
        return []

    album = check_album(resp.response_json, globalconstants.__discogs__())

    if album['album'] and album['artist']:
        if util.clean_input_str("\nis the above correct (y/n)? ", True) == globalconstants.__yes__():
            return get_album_data_from_source(album, resp.response_json)

    return []

def retry_switch(choice, album_query="") -> list[Song]:
    '''Switch statement for retries. Refer to retry().'''
    if choice == globalconstants.__retry__() and album_query not in "":
        return valid_discogs_flow(album_query)

    if choice == globalconstants.__manualsearch__():
        return manual_search(True)

    if choice == globalconstants.__manualentry__():
        return manual_entry()

    return []

def retry(album_query:str = "", discogs_failed:bool = False) -> list[Song]:
    '''
        Fallback if a search fails.

        retry is called again if an exception is encountered.
    '''
    try:
        choices = deque([globalconstants.__retry__(), globalconstants.__manualsearch__(), globalconstants.__manualentry__()])

        if discogs_failed:
            choices.popleft()

        prompts.retry_choice_prompt(discogs_failed)

        sel = util.clean_input_int("selection: ")
        if sel < 1 or sel > len(choices):
            raise ValueError("menu option does not exist...")

        if len(choices) == 2 and album_query in "":
            return retry_switch(choices[sel - 1])
        
        return retry_switch(choices[sel - 1], album_query)

    except (IndexError, ValueError) as e:
        print("Invalid selection was made...Try again.")

        oe = OdnoException(message="Invalid selection...", e=e)
        OdnoException.handle_exception(self=oe, description=oe.message, caller=f"{MODULE_NAME}.retry")

        return retry(album_query, discogs_failed)

def manual_search(is_retry:bool = False) -> list[Song]:
    '''
        Prompt user to perform a manual search if an automated one can't be done or returns undesirable results.
    '''
    q = util.clean_input_str("\nWould you like to do a manual search (y/n)? ", True) if not is_retry else globalconstants.__yes__()
    if q.lower() == globalconstants.__yes__():

        artist_name = odno_cache.get('artist') if odno_cache.get('artist') else util.clean_input_str("\nenter artist name: ")
        album_name = odno_cache.get('album') if odno_cache.get('album') else util.clean_input_str("\nenter artist name: ")

        print(f"\nsearching for {album_name} by {artist_name}")

        artist_name.replace(" ", "+")
        album_name.replace(" ", "+")

        resp = fetcher.get_album_lastfm(artist_name, album_name)

        if not resp.is_success:
            print("Album data could not be found...")
            resp.show_errors()
            prompts.wow_niche()
            return []

        album = check_album(resp.response_json, globalconstants.__lastfm__())
        if (album["album"] not in "" and album["artist"] not in "") and util.clean_input_str("\nis the above correct (y/n)? ", True) == globalconstants.__yes__():
            return get_album_data_from_source(album, resp.response_json)

    prompts.wow_niche()
    return []

def manual_entry(dir_list:list=None, is_retry:bool = False) -> list[Song]:
    '''Allow user to enter track metadata via inputs as a fallback if fetchers return no result.'''
    try:
        if is_retry and util.clean_input_str("\nEnter metadata manually (y/n)? ", True) == globalconstants.__no__():
            return []

        if dir_list is None:
            dir_list = []

        tracks = []
        album_len = util.clean_input_int("\nNumber of tracks: ") if not dir_list else len(dir_list)

        artist_name = odno_cache.get('artist') if odno_cache.get('artist') else util.clean_input_str("\nenter artist name: ")
        album_name = odno_cache.get('album') if odno_cache.get('album') else util.clean_input_str("\nenter album name: ")

        artist_name.replace(" ", "+")
        album_name.replace(" ", "+")

        genre = util.clean_input_str("\ngenre: ")
        year = util.convert_date_str(util.clean_input_str("\nyear (mm/dd/yyyy): "))
	
	# TODO: test what happens when a bad url is provided.
        cover = util.clean_input_str("\nProvide album image url (optional | most image url links from search engine are supported): ")

        track_num = 1
        while track_num <= album_len:
            name = util.clean_input_str(f'track {track_num} name: ')

            song = (SongBuilder()
                    .title(name)
                    .album(album_name)
                    .artist(artist_name)
                    .album_artist(artist_name)
                    .genre(genre)
                    .track_num(track_num)
                    .year(year)
                    .cover(cover)
                    .build())

            tracks.append(song)
            track_num += 1

    except (ValueError, TypeError) as e:
        print("ERROR: invalid input...")

        oe = OdnoException("invalid input", e)
        OdnoException.handle_exception(oe, oe.message, f"{MODULE_NAME}.manual_entry")

    return tracks

def get_response_from_repo(album_query:str) -> ResponseBody:
    '''
        program api to query web services for album metadata.
        
        parameters:
            *album_query -> album query string
    '''

    resp = ResponseBody()

    query = album_query.split("-")
    artist_str = query[-1].replace(" ", "+").replace("_","+")
    album_str = query[0].replace(" ", "+").replace("_", "+")

    resp = fetcher.get_album_lastfm(artist_str, album_str)

    if not resp.is_success:
        print("Album could not be found.")
        result_list = retry(album_query, False)
        if result_list:
            resp.result_list = result_list
            resp.is_success = True
        else:
            print("Retry failed...")

    else:
        print(f'\nsearching for {query[0]} by {query[1]}')
        album = check_album(resp.response_json, globalconstants.__lastfm__())

        q:str = util.clean_input_str("\nis the above correct (y/n)? ", True)
        if q == globalconstants.__yes__():
            print("getting album metadata...\n")
            result_list = get_album_data_from_source(album, resp.response_json)
            if result_list:
                resp.result_list = result_list

            else:
                print("album data could not be retrieved from source...")

        elif q.lower() == globalconstants.__no__() and util.clean_input_str("try again (y/n)? ", True) == globalconstants.__yes__():
            result_list = retry(album_query, False)
            if result_list:
                resp.result_list = result_list

            else:
                print("discogs list came back empty...")

    if not resp.result_list:
        resp.reset()

    return resp

def get_album_image(path:str, album_url:str) -> bool:
    '''
        Download album from URL string.

        parameters:
            * path -> path to save album cover
            * album_url -> album url as string

        return:
            bool if save is succesful or not.
    '''
    try:

        if "discogs" in album_url:
            print("discogs blocks requests to image files. skipping.")
            return False

        with open(os.path.join(path,"cover.jpg"), "wb") as image:
            data = requests.get(album_url, stream=True, timeout=20)
            if not data.ok:
                print('failed to get image from server - %s', data.status_code)
                return False

            for img in data.iter_content(1024):
                if not img:
                    print('failed to get image from server - data chunk came back None')
                    return False

                image.write(img)

            print(f'downloading image from {album_url}...')

        return True

    except OSError as e:
        print("failed to save image.")

        odnologger.log(log_level="ERROR", msg="failed to save image...", e=e, module_name=f'{MODULE_NAME}.get_album_image')

        oe = OdnoException("failed to save image", e)
        OdnoException.handle_exception(oe, oe.message, f"{MODULE_NAME}.get_album_image")

        return False


def modify_metadata_ffmpeg(path:str, file:str, song:Song, convert_opts:list, is_saved:bool) -> bool:
    '''
        Format a series of ffmpeg commands to add metadata to audio files.
        Yup, this bad boy is an ffmpeg wrapper.
    '''
    try:
        ftype = file.split(".")[-1]
        is_mp3 = True if ftype == globalconstants.__mp3__() else False
        is_convert: bool = convert_opts[0]

        parent_dir = os.path.join(os.path.dirname(path), globalconstants.__tmpdir__())

        source_file = os.path.join(os.path.dirname(parent_dir), file) if " " not in file else os.path.join(os.path.dirname(parent_dir), f"'{file}'")

        title = f'{"".join(e for e in song.title if e.isalnum())}.{ftype}'
        dest_file = os.path.join(path, title)

        new_mp3_title = f'{title.split(".", maxsplit=1)[0]}.mp3'

        og = os.path.join(path, new_mp3_title) if is_convert else dest_file
        final_file = os.path.join(dest_file.split(title)[0] , f'{song.track_num}_{new_mp3_title}') if is_convert else os.path.join(dest_file.split(title)[0] , f'{song.track_num}_{title}')

        cmds.cp_cmd(source_file, dest_file)

        if not is_mp3 and is_convert:
            bit_rate: int = convert_opts[1]
            if bit_rate == 0:
                raise ValueError("ERROR: invalid bit_rate...")

            cmds.convert_cmd(source_file, bit_rate, og)

        cmds.add_meta_data_ffmpeg_cmd(is_saved, og, parent_dir, song, final_file)

        if is_convert:
            cmds.clean_up_cmd(og)

    except (ValueError, TypeError, TimeoutError) as e:
        print("failed to convert files...")

        oe = OdnoException("failed to convert files", e)
        OdnoException.handle_exception(oe, oe.message, f"{MODULE_NAME}.modify_metadata_ffmpeg")

        return False

    return True

def manual_fallback() -> list[Song]:
    '''Call manual methods if search methods fail.'''
    tracks = manual_search()
    if not tracks:
        tracks = manual_entry()
    
    return tracks

def auto_search(album_name:str) -> list[Song]:
    '''Search for album metadata using provided album directory.'''
    odno_response = get_response_from_repo(album_name)

    if not odno_response.is_success:
        if globalconstants.__debugflg__():
            odno_response.show_errors()
        print("Could not get album data...")

    return odno_response.result_list

def save_album_metadata(tracks:list[Song], dir_list:deque, tmp:str = "") -> bool:
    '''write metadata to files using FFMPEG'''
    odnologger.log(msg=f"\ntrack list: {dir_list}", module_name=f'{MODULE_NAME}.save_album_metadata')

    success = False
    is_saved = False

    is_convert = prompts.do_convert()

    conversion = [is_convert, 0]
    if is_convert:
        conversion[1] = prompts.get_bit_rate()

    for i in tracks:
        if not is_saved and i.cover not in "":
            is_saved = get_album_image(tmp, i.cover)

        if dir_list:
            dir_track = dir_list.popleft()
            success = modify_metadata_ffmpeg(tmp, dir_track, i, conversion, is_saved)

        if not success:
            print("conversion failed...")
            break

    if success:
        util.remove_wavs(tmp)

    return success



def do_process(selection:int = 0) -> bool:
    '''
        Perform APP function based on user input.
        
        returns:
            * bool based on success
    '''
    if selection == 0 or not isinstance(selection, int):
        OdnoException.handle_exception(
            OdnoException("Invalid selection...",
                          ValueError("choose a correct value from the menu.")),
                          f"{MODULE_NAME}.do_process")

    if selection == 1:
        prompts.show_help()
        return False
    else:
        path = odno_cache.get('album_dir', None)
        if not path:
            path = util.clean_input_str("enter album file path to get started: ")

        tmp:str = os.path.join(path, globalconstants.__tmpdir__())

        odnologger.log(msg=f"tmp_dir: {tmp}", module_name=f'{MODULE_NAME}.save_album_metadata')

        if os.path.exists(tmp):
            subprocess.call(f"rm -r {tmp}",shell=True)

        dir_list = odno_cache.get('dir_list', os.listdir(path))
        util.sort_tracks(dir_list)

        dir_list = deque(dir_list)

        os.mkdir(tmp)

        tracks = []
        if os.path.exists(path) and os.path.isdir(path):
            if selection == 2:
                album = odno_cache.get('album', None)
                artist_name = odno_cache.get('artist', None)
                if album and artist_name:
                    album_name = f"{album}-{artist_name}"
                    
                else:
                    album_name = path.split("/")[-1]

                tracks = auto_search(album_name)

            elif selection == 3:
                tracks = manual_search(True)

            elif selection == 4:
                tracks = manual_entry()

            if not tracks:
                tracks = retry(discogs_failed=True)
                if not tracks:
                    return False

            return save_album_metadata(tracks, dir_list, tmp)

    return False
