import os
import requests
import subprocess

from collections import deque

from src.fetcher import get_album_discogs, get_album_lastfm, fetch_date_from_music_brainz
from src.models import Song
from src.utility import sort_tracks, get_bit_rate, remove_wavs
from src.prompts import wow_niche, save_metadata_ffmpeg, convert_to_mp3_with_selected_bitrate, clean_up, copy_to_temp

TMP_DIR = "MP3_ALBUM"

def check_album(album:dict, platform:str) -> dict:
    '''
        Helper function to get album metadata from Spotify.search() and display album, artist, & release date.

        parameters:
            * album -> JSON object from discogs_client.Client(*args).search()
    '''
    tmp = {
        "album" : "",
        "artist": "",
        "release_date": ""
    }

    if platform == "LASTFM":
        mbid = album['album']['mbid']
        tmp["album"] = album['album']['name']
        tmp['artist'] = album['album']['artist']
        tmp["release_date"] =  fetch_date_from_music_brainz(mbid,False)
    
    elif platform == "DISCOGS":
        tmp["album"] = album['title']
        tmp['artist'] = album['artists'][0]['name']
        tmp["release_date"] = album['year']
    
    print(
        "album:",   tmp['album']           +"\n",
        "artist:",  tmp['artist']          +"\n",
        "release:", str(tmp['release_date'])    +"\n"
    )

    return tmp

def get_album_data_from_discogs(album:dict, resp:dict, debug:bool) -> list[Song]:
    '''
        retrieve album data from discogs database.
    '''
    
    tracks = []

    album_cover = resp['images'][0]['uri']
    genre = resp['styles'][0] if len(resp['styles']) > 1 else resp['genres'][0]

    l = len(resp['tracklist'])
    for t in range(l):
        song = Song(
            title=resp["tracklist"][t]['title'],
            artist=album['artist'],
            album_artist=album['artist'],
            album=album['album'],
            cd = 1,
            genre=genre,
            year=resp['year'],
            track_num= t + 1,
            cover = album_cover
        )

        tracks.append(song)

    if debug:
        print("response:", resp)
    
    return tracks

def get_album_data_from_lastfm(album:dict, resp:dict, debug:bool) -> list[Song]:
    '''
        retrieve album data from lastfm database.
    '''
    
    tracks = []
    
    try:
        if debug:
            print(resp)
            print(album)

        album_cover = "" 
        genre = ""
        if len(resp['album']['image']) > 0:
            album_cover = resp['album']['image'][3]["#text"]

        if resp['album']["tags"] != "":
            genre = resp['album']["tags"]["tag"][0]["name"]

        release = album['release_date']

        track_num = 1
        for t in resp["album"]["tracks"]["track"]:
            song = Song(
                title = t['name'],
                artist = album['artist'],
                album_artist= album['artist'],
                album = album['album'],
                cd=1,
                genre=genre,
                year= release,
                track_num = track_num,
                cover = album_cover
            )
            track_num += 1
            tracks.append(song)

        if debug:
            print()
            print(tracks)

    except KeyError as ke:
        print("album data could not be retrieved...")
        if debug:
            print("KeyError in JSON response:",ke)
    
    return tracks

def manual_search() -> list[Song]:
    '''
        Prompt user to perform a manual search if an automated one can't be done or returns undesirable results.
    '''
    q = input("Would you like to do a manual search (y/n)? ")
    if q.lower() == "y":
        artist_name = input("enter artist name: ")
        album_name = input("enter album name: ")

        print(f"\n searching for {album_name} by {artist_name}")
        resp = get_album_lastfm(artist_name, album_name, True)

        album = check_album(resp, "LASTFM")

        q = input("is the above correct (y/n)? ")
        if q.lower() == "y":
            return get_album_data_from_lastfm(album, resp, True)

        wow_niche()
        return []

    return []

def get_album_from_repo(album_query:str, debug:bool) -> list[Song]:
    '''
        program api to query web services for album metadata.
        
        parameters:
            *album_query -> album query string
            *debug -> turn debug on
    '''

    resp: dict = {}

    query = album_query.split("-")
    artist_str = query[-1].replace(" ", "+").replace("_","+")
    album_str = query[0].replace(" ", "+").replace("_", "+")
    
    resp = get_album_lastfm(artist_str, album_str, debug)
    
    print(f"\nsearching for {album_query}.")
    album = check_album(resp, "LASTFM")
    
    q:str = input("is the above correct (y/n)? ")
    if q.lower() == "y":
        print("getting album metadata...\n")
        return get_album_data_from_lastfm(album, resp, debug)

    if q.lower() == "n":
        q = input("try again (y/n)? ")
        if q.lower() == "y":
            album_query = album_query.replace("-", " by ").replace("_", " ")
            resp = get_album_discogs(album_query)
            album = check_album(resp, "DISCOGS")
            
            q = input("is the above correct (y/n)?")
            if q.lower() == "y":
                return get_album_data_from_discogs(album, resp, debug)
    
    return []

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
                print(f'failed to get image from server - error: {data.status_code}')
                return False
            
            for img in data.iter_content(1024):
                if not img:
                    print('failed to get image from server - error: data chunk came back None')
                    return False
                
                print(f'downloading image from {album_url}...')
                image.write(img)
            
        return True
    except OSError as e:
        print("failed to save image.")
        print(e)
        return False


def modify_metadata_ffmpeg(path:str, file:str, song:Song, bit_rate:int, is_saved:bool, debug) -> bool:
    '''
        Format a series of ffmpeg commands to add metadata to audio files.
        Yup, this bad boy is an ffmpeg wrapper.
    '''
    
    # ftype = file.split(".")
    try:
        ftype = file.split(".")[-1]
        is_mp3 = True if ftype == "mp3" else False

        parent_dir = os.path.join(os.path.dirname(path), TMP_DIR)

        source_file = os.path.join(os.path.dirname(parent_dir), file) if " " not in file else os.path.join(os.path.dirname(parent_dir), f"'{file}'")

        title = f'{"".join(e for e in song.title if e.isalnum())}.{ftype}'
        dest_file = os.path.join(path, title)

        new_mp3_title = f'{title.split(".", maxsplit=1)[0]}.mp3'

        og = os.path.join(path, new_mp3_title) if not is_mp3 else dest_file
        final_mp3_file = os.path.join(dest_file.split(title)[0] , f'{song.track_num}_{new_mp3_title}')

        cp_cmd = copy_to_temp(source_file, dest_file)
        print(cp_cmd, "\n") if debug else ""
        subprocess.run([cp_cmd], shell=True, check=False)

        if not is_mp3:
            convert = convert_to_mp3_with_selected_bitrate(source_file, bit_rate, og)
            print(convert, "\n") if debug else print()
            subprocess.run([convert], shell=True, check = False)

        ffmpeg_meta_cmd = save_metadata_ffmpeg(is_saved, og, parent_dir, song, final_mp3_file)
        print(ffmpeg_meta_cmd, "\n") if debug else print()
        subprocess.run([ffmpeg_meta_cmd], shell=True, check = False)

        rm_cmd = clean_up(og)
        print(rm_cmd,"\n") if debug else print()
        subprocess.run([f'rm {og}'], shell=True, check=False)
    
    except Exception as e:
        print("failed...")
        
        if debug:
            print(e)
        
        return False

    return True

def save_album_metadata(debug:bool) -> bool:
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

        print("searching for:",album_name)
        
        tmp:str = os.path.join(path, TMP_DIR)
        
        if debug:
            print("tmp_dir:", tmp)

        if os.path.exists(tmp):
            subprocess.call(f"rm -r {tmp}",shell=True)
        
        dir_list = os.listdir(path)
        sort_tracks(dir_list)

        dir_list = deque(dir_list)

        os.mkdir(tmp)

        if debug:
            print("\ntrack list:",dir_list)

        tracks = get_album_from_repo(album_name, debug)
        if len(tracks) == 0:
            tracks = manual_search()
            if len(tracks) == 0:
                return False

        bit_rate = get_bit_rate()

        is_saved = False
        for i in tracks:
            if not is_saved:
                is_saved = get_album_image(tmp, i.cover)
            dir_track = dir_list.popleft()
            success = modify_metadata_ffmpeg(tmp, dir_track, i, bit_rate, is_saved, debug)

            if not success:
                print("conversion failed...")
                break
    
    if success:
        remove_wavs(tmp)

    return success

if __name__ == "__main__":
    # query:str = "daydream nation by sonic youth"

    # tracks:list[Song] = get_album_from_repo(query, True)
    # # print(tracks)

    # print("\n\ntracks:")
    # for t in tracks:
    #     print(t)

    save_album_metadata(True)