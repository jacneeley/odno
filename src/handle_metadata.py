'''common module for handling application flow.'''
import os
import requests
import subprocess
import time
import re
import sys

from collections import deque, namedtuple
from concurrent.futures import ThreadPoolExecutor

import core.utility as util
import view.prompts as prompts
import core.cmds as cmds
from core.odno_logging import odnologger
from exceptions.odno_exceptions import OdnoException
from core.odno_cache import odno_cache

import src.global_constants as global_constants
import src.fetcher as fetcher
from src.models import SongBuilder, Song, ResponseBody

MODULE_NAME = "handle_metadata"

_track_struct = namedtuple("track_struct", "path file")
__track:_track_struct = None

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
        if platform == global_constants.__lastfm__():
            mbid = album['album']['mbid']
            tmp["album"] = album['album']['name']
            tmp['artist'] = album['album']['artist']
            tmp['release_date'] =  fetcher.fetch_date_from_music_brainz(mbid)
            tmp['source'] = global_constants.__lastfm__()

        elif platform == global_constants.__discogs__():
            tmp['album'] = album['title']
            tmp['artist'] = album['artists'][0]['name']
            tmp['release_date'] = util.convert_date_str(album['year'])
            tmp['source'] = global_constants.__discogs__()

        print("album:",    tmp['album'])
        print("artist:",   tmp['artist'])
        print("release:",  str(tmp['release_date']))

    except (KeyError, ValueError) as e:
        if isinstance(KeyError, e):
            print("Album could not be found...")
            msg = "Album could not be found in lastfm response." if platform == global_constants.__lastfm__() else "Album could not be found in discogs response."
        else:
            print("Error Ocurred")
            msg = "issue parsing dates."
        oe = OdnoException(msg, e)
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

        if source == global_constants.__discogs__():
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

    album = check_album(resp.response_json, global_constants.__discogs__())

    if album['album'] and album['artist']:
        if util.clean_input_str("\nis the above correct (y/n)? ", True) == global_constants.__yes__():
            return get_album_data_from_source(album, resp.response_json)

    return []

def retry_switch(choice, album_query="") -> list[Song]:
    '''Switch statement for retries. Refer to retry().'''
    if choice == global_constants.__retry__() and album_query not in "":
        return valid_discogs_flow(album_query)

    if choice == global_constants.__manualsearch__():
        return manual_search(True)

    if choice == global_constants.__manualentry__():
        return manual_entry()

    return []

def retry(album_query:str = "", discogs_failed:bool = False) -> list[Song]:
    '''
        Fallback if a search fails.

        retry is called again if an exception is encountered.
    '''
    try:
        choices = deque([global_constants.__retry__(), global_constants.__manualsearch__(), global_constants.__manualentry__()])

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
    q = util.clean_input_str("\nWould you like to do a manual search (y/n)? ", True) if not is_retry else global_constants.__yes__()
    if q.lower() == global_constants.__yes__():

        artist_name = odno_cache.get('artist_name') if odno_cache.get('artist_name', "") else util.clean_input_str("\nenter artist name: ")
        album_name = odno_cache.get('album_name') if odno_cache.get('album_name', "") else util.clean_input_str("\nenter album name: ")

        print(f"\nsearching for {album_name} by {artist_name}")

        artist_name.replace(" ", "+")
        album_name.replace(" ", "+")

        resp = fetcher.get_album_lastfm(artist_name, album_name)

        if not resp.is_success:
            print("Album data could not be found...")
            resp.show_errors()
            prompts.wow_niche()
            return []

        album = check_album(resp.response_json, global_constants.__lastfm__())
        if (album["album"] not in "" and album["artist"] not in "") and util.clean_input_str("\nis the above correct (y/n)? ", True) == global_constants.__yes__():
            return get_album_data_from_source(album, resp.response_json)

    prompts.wow_niche()
    return []

def manual_entry(dir_list:list=None, is_retry:bool = False) -> list[Song]:
    '''Allow user to enter track metadata via inputs as a fallback if fetchers return no result.'''
    try:
        if is_retry and util.clean_input_str("\nEnter metadata manually (y/n)? ", True) == global_constants.__no__():
            return []

        if dir_list is None:
            dir_list = []

        tracks = []
        album_len = util.clean_input_int("\nNumber of tracks: ") if not dir_list else len(dir_list)

        artist_name = odno_cache.get('artist_name') if odno_cache.get('artist_name', "") else util.clean_input_str("\nenter artist name: ")
        album_name = odno_cache.get('album_name') if odno_cache.get('album_name', "") else util.clean_input_str("\nenter album name: ")

        artist_name.replace(" ", "+")
        album_name.replace(" ", "+")

        genre = util.clean_input_str("\ngenre: ")
        year = util.convert_date_str(util.clean_input_str("\nyear (mm/dd/yyyy): "))

	    # TODO: test what happens when a bad url is provided.
        cover = odno_cache.get('img',
            util.clean_input_str("\nProvide album image url (optional | most image url links from search engine are supported): "))

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
        album = check_album(resp.response_json, global_constants.__lastfm__())

        q:str = util.clean_input_str("\nis the above correct (y/n)? ", True)
        if q == global_constants.__yes__():
            print("getting album metadata...\n")
            result_list = get_album_data_from_source(album, resp.response_json)
            if result_list:
                resp.result_list = result_list

            else:
                print("album data could not be retrieved from source...")

        elif q.lower() == global_constants.__no__() and util.clean_input_str("try again (y/n)? ", True) == global_constants.__yes__():
            result_list = retry(album_query, False)
            if result_list:
                resp.result_list = result_list

            else:
                print("discogs list came back empty...")

    if not resp.result_list:
        resp.reset()

    return resp

def get_album_image(path:str, album_cover_url:str) -> None:
    '''
        Download album from URL string.

        parameters:
            * path -> path to save album cover
            * album_url -> album url as string

        return:
            bool if save is succesful or not.
    '''
    try:
        if album_cover_url in "":
            odno_cache['img_saved'] = False
            return
        
        if "discogs" in album_cover_url:
            print("discogs blocks requests to image files. skipping.")
            odno_cache['img_saved'] = False
            return

        with open(os.path.join(path,"cover.jpg"), "wb") as image:
            data = requests.get(album_cover_url, stream=True, timeout=20)
            if not data.ok:
                print('failed to get image from server - %s', data.status_code)
                return False

            for img in data.iter_content(1024):
                if not img:
                    print('failed to get image from server - data chunk came back None')
                    odno_cache['img_saved'] = False
                    return

                image.write(img)

            print(f'downloading image from {album_cover_url}...')

        odno_cache['img_saved'] = True

    except OSError as e:
        print("failed to save image.")

        odnologger.log(log_level="ERROR", msg="failed to save image...", e=e, module_name=f'{MODULE_NAME}.get_album_image')

        oe = OdnoException("failed to save image", e)
        OdnoException.handle_exception(oe, oe.message, f"{MODULE_NAME}.get_album_image")

        odno_cache['img_saved'] = False

def copy_tracks_to_dest(source:str, dest:str, save_as:str) -> _track_struct:
    '''move track to tmp folder for processing'''
    ftype = source.split(".")[-1]

    dest_file = f'{dest}/{save_as}.{ftype}'

    try:
        cmds.cp_cmd(source, dest_file)
        return _track_struct(source, dest_file)
    except OdnoException as oe:
        OdnoException.handle_exception(oe, oe.message, f'{MODULE_NAME}.copy_tracks_to_dest')
        print("failed to copy tracks.")
        sys.exit()


def convert_track(source:str, convert_opts:list) -> bool:
    '''Convert tracks if user desires'''
    try:
        new_mp3 = source.replace(".wav", ".mp3")

        bit_rate:int = convert_opts[1]
        if bit_rate == 0:
            raise ValueError("ERROR: invalid bit_rate...")

        cmds.convert_cmd(source, bit_rate, new_mp3)

        return True

    except (ValueError, OdnoException) as e:
        caller = f'{MODULE_NAME}.convert_track'
        if isinstance(ValueError, e):
            OdnoException.handle_exception(OdnoException(f"Could not convert track {source} to {new_mp3}.", e), e.__cause__, caller)
        else:
            OdnoException.handle_exception(e, e.message, caller)

        print(f"failed to convert - {e.message}. exiting.")
        return False

def modify_metadata_ffmpeg(source:str, song:Song, is_saved:bool, is_convert:bool = False) -> bool:
    '''
        Format a series of ffmpeg commands to add metadata to audio files.
        Yup, this bad boy is an ffmpeg wrapper.
    '''
    try:
        final = source.split(".")
        final_file = f'{final[0]}_final.{final[1]}'

        cmds.add_meta_data_ffmpeg_cmd(is_saved, source, odno_cache["album_path_tmp"], song, final_file)

        if is_convert:
            cmds.clean_up_cmd(source)

        return True

    except (ValueError, TypeError, TimeoutError, OdnoException) as e:
        print("failed to convert files...")

        caller = f"{MODULE_NAME}.modify_metadata_ffmpeg"

        if isinstance(OdnoException, e):
            OdnoException.handle_exception(e, e.message, caller)

        else:
            oe = OdnoException("failed to convert files", e)
            OdnoException.handle_exception(oe, oe.message, caller)

        return False

def manual_fallback(is_retry:bool = False) -> list[Song]:
    '''Call manual methods if search methods fail.'''
    if is_retry:
        return manual_entry()

    tracks = manual_search()
    if not tracks:
        tracks = manual_entry()
    
    return tracks

def auto_search(album_name:str) -> list[Song]:
    '''Search for album metadata using provided album directory.'''
    odno_response = get_response_from_repo(album_name)

    if not odno_response.is_success:
        if global_constants.__debugflg__():
            odno_response.show_errors()
        print("Could not get album data...")

    return odno_response.result_list

def process_tracks(tracks, conversion, dir_list):
    '''prepare and convert tracks'''
    parent = odno_cache.get("album_path", "")
    tmp = odno_cache.get("album_path_tmp","")

    if parent in "" or tmp in "":
        print("tracks could not be processed. Album directory not found...")
        return

    if not dir_list:
        print("Tracks could not be found in directory. Directory is empty...")
        return

    pattern = "[^a-zA-Z0-9_]"
    for i, j in enumerate(tracks):
        source = f'{parent}/{dir_list[i]}' if parent[-1] != "/" else f'{parent}{dir_list[i]}'
        _track = copy_tracks_to_dest(source, tmp, f'{j.track_num}_{re.sub(pattern=pattern, repl="", string=j.title)}')
        if conversion[0]:
            convert_track(_track.file, conversion)
            cmds.clean_up_cmd(_track.file)

def save_album_metadata(tracks:list[Song], dir_list:deque) -> bool:
    '''write metadata to files using FFMPEG'''
    start = time.time()
    odnologger.log(msg=f"\ntrack list: {dir_list}", module_name=f'{MODULE_NAME}.save_album_metadata')

    success = False
    tmp = odno_cache.get("album_path_tmp", "")

    if tmp in "":
        raise FileNotFoundError("ALBUM directory could not be found...")

    is_convert = prompts.do_convert(global_constants.__mp3__() in dir_list)

    conversion = [is_convert, 0]
    if is_convert:
        conversion[1] = prompts.get_bit_rate()

    with ThreadPoolExecutor() as executor:
        executor.submit(get_album_image, tmp, tracks[0].cover)

    if len(tracks) < 3:
        process_tracks(tracks, conversion, dir_list)
    else:
        if len(dir_list) != len(tracks):
            if tracks[0].cover:
                odno_cache['img'] = tracks[0].cover
            ans = input("\nUnknown ERROR: The length of tracks doesn't match the number of tracks found online\nYou might have a special version. Try Manual Entry (y/n)?")
            if ans == global_constants.__yes__():
                manual_fallback(is_retry=True)
            return False

        mid = int((len(tracks) -1 ) / 2)
        # source1 = list(dir_list)[:mid]
        # source2 = list(dir_list)[mid:]
        source1 = []
        count = 0
        while dir_list and count < mid:
            count += 1
            source1.append(dir_list.popleft())

        source2 = []
        while dir_list:
            source2.append(dir_list.popleft())

        tracks1 = tracks[:mid]
        tracks2 = tracks[mid:]

        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(process_tracks, tracks1, conversion, source1)
            executor.submit(process_tracks, tracks2, conversion, source2)

        executor.shutdown(wait=True)

    dir_list = os.listdir(odno_cache["album_path_tmp"])
    util.sort_tracks(dir_list)
    dir_list = deque(dir_list)

    parent = odno_cache["album_path_tmp"]
    for i in tracks:
        if dir_list:
            dir_track = dir_list.popleft()
            source = f'{parent}/{dir_track}'
            success = modify_metadata_ffmpeg(source, i, odno_cache['img_saved'], conversion[0])

        if not success:
            print("conversion failed...")
            break

    end = time.time()
    print(f"\nconversion time:{end - start} seconds")

    return success

def do_process(selection:int = 0) -> bool:
    '''
        Perform APP function based on user input.
        
        returns:
            * bool based on success
    '''
    path = odno_cache.get('album_dir', None)
    if not path:
        path = util.clean_input_str("enter album file path to get started: ")
        odno_cache['album_path'] = path

    tmp:str = os.path.join(path, global_constants.__tmpdir__())

    odnologger.log(msg=f"tmp_dir: {tmp}", module_name=f'{MODULE_NAME}.save_album_metadata')

    if os.path.exists(tmp):
        subprocess.call(f"rm -r {tmp}",shell=True)

    dir_list = odno_cache.get('dir_list', os.listdir(path))
    util.sort_tracks(dir_list)

    dir_list = deque(dir_list)
    odno_cache['dir_list'] = dir_list

    os.mkdir(tmp)
    if not os.path.exists(tmp):
        print("Directory could not be found...")
        return False

    odno_cache["album_path_tmp"] = tmp

    tracks = []
    if os.path.exists(path) and os.path.isdir(path):
        if selection == 1:
            album = odno_cache.get('album', None)
            artist_name = odno_cache.get('artist', None)
            if album and artist_name:
                album_name = f"{album}-{artist_name}"

            else:
                album_name = path.split("/")[-1]

            tracks = auto_search(album_name)

        elif selection == 2:
            tracks = manual_search(True)

        elif selection == 3:
            tracks = manual_entry()

        if not tracks:
            tracks = retry(discogs_failed=True)
            if not tracks:
                return False

        return save_album_metadata(tracks, dir_list)

    return False
