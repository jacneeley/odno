import os
import requests
import subprocess

from collections import deque

import src.fetcher as fetcher
import src.utility as util
import src.prompts as prompts
from src.models import SongBuilder, Song, ResponseBody
import scripts.globalconstants as globalconstants
import scripts.odnologging as odnologging

logger = odnologging.create_logger("handle_metadata.py")

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

    return tmp

def get_album_data_from_source(album:dict, resp:dict) -> list[Song]:
    '''
        retrieve album data from source.
    '''

    tracks = []

    try:
        if globalconstants.__debugflg__():
            logger.info(resp)
            logger.info(album)

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

        if globalconstants.__debugflg__():
            logger.info(tracks)

    except KeyError as ke:
        logger.error("album data could not be retrieved...")
        if globalconstants.__debugflg__():
            logger.error("KeyError in JSON response: %s", ke)

    except ValueError as ve:
        logger.error("album data could not be retrieved...")
        if globalconstants.__debugflg__():
            logger.error("ValueError ocurred building Song: %s", ve)

    return tracks

def valid_discogs_flow(album_query:str) -> list[Song]:
    '''Application will check discogs if lastfm search fails or returns incorrect results.'''
    album_query = album_query.replace("-", " by ").replace("_", " ")
    resp = fetcher.get_album_discogs(album_query)

    if not resp.is_success:
        logger.error("Album data could not be found...")
        if resp.exception and resp.debug:
            for e in resp.exception:
                logger.exception(e)
        return []

    album = check_album(resp.response_json, globalconstants.__discogs__())

    if input("is the above correct (y/n)?").lower() == globalconstants.__yes__():
        return get_album_data_from_source(album, resp.response_json)

    return []

def retry_switch(choice, album_query) -> list[Song]:
    '''Switch statement for retries. Refer to retry().'''
    if choice == globalconstants.__retry__():
        return valid_discogs_flow(album_query)

    if choice == globalconstants.__manualsearch__():
        return manual_search()

    if choice == globalconstants.__manualentry__():
        return [] ##TODO: create manual entry

    return []

def retry(album_query:str, discogs_failed:bool) -> list[Song]:
    '''Fallback if a search fails.'''
    try:
        choices = deque([globalconstants.__retry__(), globalconstants.__manualsearch__(), globalconstants.__manualentry__()])

        if discogs_failed:
            choices.popleft()

        prompts.retry_choice_prompt(discogs_failed)

        sel = int("selection: ")
        return retry_switch(choices[sel], album_query)

    except IndexError:
        logger.error("Invalid selection was made...Try again.")
        retry(album_query, discogs_failed)

def manual_search() -> list[Song]:
    '''
        Prompt user to perform a manual search if an automated one can't be done or returns undesirable results.
    '''
    q = input("Would you like to do a manual search (y/n)? ")
    if q.lower() == globalconstants.__yes__():
        artist_name = input("enter artist name: ")
        album_name = input("enter album name: ")

        print(f"\n searching for {album_name} by {artist_name}")
        resp = fetcher.get_album_lastfm(artist_name, album_name)

        album = check_album(resp.response_json, globalconstants.__lastfm__())

        q = input("is the above correct (y/n)? ")
        if q.lower() == globalconstants.__yes__():
            return get_album_data_from_source(album, resp.response_json)

        prompts.wow_niche()
        return []

    return []

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
        logger.warning("Album could not be found.")
        result_list = retry(album_query, False)
        if result_list:
            resp.result_list = result_list
            resp.is_success = True
        elif globalconstants.__debugflg__():
            logger.error("Retry failed...")

    else:
        print("searching for %s", album_query)
        album = check_album(resp.response_json, globalconstants.__lastfm__())

        q:str = input("is the above correct (y/n)? ")
        if q.lower() == globalconstants.__yes__():
            print("getting album metadata...\n")
            result_list = get_album_data_from_source(album, resp.response_json)
            if result_list:
                resp.result_list = result_list
            elif globalconstants.__debugflg__():
                logger.error("album data could not be retrieved from source...")

        elif q.lower() == globalconstants.__no__() and input("try again (y/n)? ").lower() == globalconstants.__yes__():
            result_list = valid_discogs_flow(album_query)
            if result_list:
                resp.result_list = result_list
            elif globalconstants.__debugflg__():
                logger.error("discogs list came back empty...")

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
                logger.warning('failed to get image from server - %s', data.status_code)
                return False

            for img in data.iter_content(1024):
                if not img:
                    logger.warning('failed to get image from server - data chunk came back None')
                    return False

                print('downloading image from %s...', album_url)
                image.write(img)

        return True

    except OSError as e:
        logger.error("failed to save image.")
        if globalconstants.__debugflg__():
            logger.exception(e)

        return False


def modify_metadata_ffmpeg(path:str, file:str, song:Song, bit_rate:int, is_saved:bool) -> bool:
    '''
        Format a series of ffmpeg commands to add metadata to audio files.
        Yup, this bad boy is an ffmpeg wrapper.
    '''

    # ftype = file.split(".")
    try:
        ftype = file.split(".")[-1]
        is_mp3 = True if ftype == globalconstants.__mp3__() else False

        parent_dir = os.path.join(os.path.dirname(path), globalconstants.__tmpdir__())

        source_file = os.path.join(os.path.dirname(parent_dir), file) if " " not in file else os.path.join(os.path.dirname(parent_dir), f"'{file}'")

        title = f'{"".join(e for e in song.title if e.isalnum())}.{ftype}'
        dest_file = os.path.join(path, title)

        new_mp3_title = f'{title.split(".", maxsplit=1)[0]}.mp3'

        og = os.path.join(path, new_mp3_title) if not is_mp3 else dest_file
        final_mp3_file = os.path.join(dest_file.split(title)[0] , f'{song.track_num}_{new_mp3_title}')

        cp_cmd = prompts.copy_to_temp(source_file, dest_file)
        if globalconstants.__debugflg__():
            logger.info("%s\n", cp_cmd)
        
        subprocess.run([cp_cmd], shell=True, check=False)

        if not is_mp3:
            convert = prompts.convert_to_mp3_with_selected_bitrate(source_file, bit_rate, og)
            if globalconstants.__debugflg__():
                logger.info("%s\n", convert)
            
            subprocess.run([convert], shell=True, check = False)

        ffmpeg_meta_cmd = prompts.save_metadata_ffmpeg(is_saved, og, parent_dir, song, final_mp3_file)
        if globalconstants.__debugflg__():
                logger.info("%s\n", ffmpeg_meta_cmd)
        
        subprocess.run([ffmpeg_meta_cmd], shell=True, check = False)

        rm_cmd = prompts.clean_up(og)
        if globalconstants.__debugflg__():
            logger.info("%s\n", rm_cmd)
        
        subprocess.run([f'rm {og}'], shell=True, check=False)

    except Exception as e:
        logger.error("failed to convert files...")

        if globalconstants.__debugflg__():
            logger.exception(e)

        return False

    return True

def save_album_metadata() -> bool:
    '''
        Consume user provided file path to prepare metadata for target album.

        Album directory should follow: "some/path/to/album_name-artist_name"

        parameters:
            *debug -> boolean show console output.
    '''

    print("For best results, make sure album folders match the following: album_name-artist_name.\n")

    path = input("enter album file path: ")

    success = False
    if os.path.exists(path) and os.path.isdir(path):
        album_name = path.split("/")[-1]

        # print("searching for: %s",album_name)

        tmp:str = os.path.join(path, globalconstants.__tmpdir__())

        if globalconstants.__debugflg__():
            logger.info("tmp_dir: %s", tmp)

        if os.path.exists(tmp):
            subprocess.call(f"rm -r {tmp}",shell=True)

        dir_list = os.listdir(path)
        util.sort_tracks(dir_list)

        dir_list = deque(dir_list)

        os.mkdir(tmp)

        if globalconstants.__debugflg__():
            logger.info("\ntrack list: %s",dir_list)

        odno_response = get_response_from_repo(album_name)

        if not odno_response.is_success:
            if globalconstants.__debugflg__():
                odno_response.show_exceptions()
            print("Could not get album data...")
            return False

        tracks = odno_response.result_list
        if len(tracks) == 0:
            tracks = manual_search()
            if len(tracks) == 0:
                ##TODO: manual_entry()
                return False

        bit_rate = prompts.get_bit_rate()

        is_saved = False
        for i in tracks:
            if not is_saved:
                is_saved = get_album_image(tmp, i.cover)
            dir_track = dir_list.popleft()
            success = modify_metadata_ffmpeg(tmp, dir_track, i, bit_rate, is_saved)

            if not success:
                print("conversion failed...")
                break

    if success:
        util.remove_wavs(tmp)

    return success

if __name__ == "__main__":
    save_album_metadata()
