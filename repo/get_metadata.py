import os
import requests
import subprocess

from repo.auth import auth_user
from song.song import Song
from util.utility import convert_date_str, sort_tracks, get_bit_rate, remove_wavs

tmp_dir = "MP3_ALBUM"

def check_album(album:dict) -> dict:
    '''
        Helper function to get album metadata from Spotify.search() and display album, artist, & release date.

        parameters:
            * album -> JSON object from Spotify.search()
    '''

    tmp = {
        "album" : "",
        "artist": "",
        "release_date": ""
    }

    tmp["album"] = album['albums']['items'][0]['name']
    tmp['artist'] = album['albums']['items'][0]['artists'][0]['name']
    tmp["release_date"] = album['albums']['items'][0]['release_date']

    print(
        "album:",   tmp['album']           +"\n",
        "artist:",  tmp['artist']          +"\n",
        "release:", tmp['release_date']    +"\n"
    )

    return tmp

def get_album_from_spotify(album_name:str, debug:bool) -> list[Song]:
    '''
        search for an album using the spotify api and get the metadata for each track.

        returns a list of Songs -> list[Song]

        parameters:
            * album_name: name of the album used to search for.
    '''
    #TODO: refactor to use a different API. Spotify will end free access to API later in March.

    resp:dict = auth_user().search(
        q=album_name,
        limit=5,
        offset=0,
        type="album",
        market="US"
    )

    tracks:list[Song] = []

    album = check_album(resp)

    q:str = input("is the above correct (y/n)? ")
    if q.lower() == "y":
        album_id = resp['albums']['items'][0]['id']
        album_cover = resp['albums']['items'][0]['images'][1]['url']

        album_tracks = auth_user().album_tracks(
            album_id=album_id,
            market="US"
        )

        print("getting album metadata...\n")
 
        for t in album_tracks['items']:
            song = Song(
                t['name'],
                album['artist'],
                album['artist'],
                album['album'],
                int(t['disc_number']),
                convert_date_str(album['release_date']),
                int(t['track_number']),
                album_cover
            )

            tracks.append(song)

            if debug:
                print("response:", resp)
                print()
                print("album tracks:",album_tracks)
                print()
                print("album items:",t)
                break
        
        return tracks

    else:
        print("done.")
        quit()

def get_album_image(path:str, album_url:str) -> bool:
    with open(os.path.join(path,"cover.jpg"), "wb") as image:
        data = requests.get(album_url, stream=True, timeout=20)
        if not data.ok:
            print(f'failed to get image from server - error: {data.status_code}')
            return False 
        
        for img in data.iter_content(1024):
            if not img:
                print(f'failed to get image from server - error: data chunk came back None')
                return False
            
            image.write(img)
        
        print(f'downloading image from {album_url}...')
    return True


def modify_metadata_ffmpeg(path:str, file:str, song:Song, bit_rate:int, is_saved:bool, debug) -> bool:
    # ftype = file.split(".")
    convert = ""
    ffmpeg_meta_cmd = ""
    
    ftype = file.split(".")[-1]
    parent_dir = os.path.join(os.path.dirname(path), tmp_dir)
    source_file = os.path.join(os.path.dirname(parent_dir), file)
    title = f'{"".join(e for e in song.title if e.isalnum())}.{ftype}'
    dest_file = os.path.join(path, title)
    
    mp3_title = f'{title.split(".")[0]}.mp3'
    og = os.path.join(path, mp3_title)

    cp_cmd = f'cp {source_file} {dest_file}'
    final_mp3_file = os.path.join(dest_file.split(title)[0] , f'{song.track_num}_{mp3_title}')
    
    convert = f'ffmpeg -i {source_file} -codec:a libmp3lame -b:a {bit_rate}k {og}'

    if is_saved:
        ffmpeg_meta_cmd = f'ffmpeg -i {og} -i {parent_dir}/cover.jpg -map 0 -map 1 -c copy -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -metadata:s:v title="{song.title} album cover" -metadata:s:v comment="{song.title} cover (front)" -disposition:v:1 attached_pic -codec copy {final_mp3_file} -hide_banner'.strip()
    else:
        ffmpeg_meta_cmd = f'ffmpeg -i {og} -i -map 0:a -map 1:v -c:a libmp3lame -b:a {bit_rate}k -id3v2_version 3 -write_id3v1 1 -metadata title="{song.title}" -metadata artist="{song.artist}" -metadata album="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata date="{song.year}" -metadata track="{song.track_num}" -codec copy {final_mp3_file} -hide_banner'.strip() 

    try:
        rm_cmd = f'rm {og}'

        print(cp_cmd, "\n") if debug else ""
        subprocess.run([cp_cmd], shell=True, check=False)
        
        print(convert, "\n") if debug else ""
        subprocess.run([convert], shell=True, check = False)
        
        print(ffmpeg_meta_cmd, "\n") if debug else ""
        subprocess.run([ffmpeg_meta_cmd], shell=True, check = False)
        
        print(rm_cmd,"\n") if debug else ""
        subprocess.run([f'rm {og}'], shell=True, check=False)
    except Exception as e:
        print("failed...")
        print(e)
        return False

    return True

def save_album_metadata(debug:bool) -> bool:
    '''

    '''

    print("For best results, make sure album folders match the following: album_name-artist_name.\n")
    
    path = input("enter album file path: ")

    success = False
    try:
        if os.path.exists(path) and os.path.isdir(path):
            album_name = path.split("/")[-1]
            album_name = album_name.replace("-", "+").replace("_", "+").replace(" ","+")

            print("searching for:",album_name)            
            
            tmp:str = os.path.join(path,tmp_dir)
            if os.path.exists(tmp):
                subprocess.call(f"rm -r {tmp}",shell=True)
            
            dir_list = os.listdir(path)
            sort_tracks(dir_list)

            os.mkdir(tmp)

            if debug:
                print("\ntrack list:",dir_list)

            tracks = get_album_from_spotify(album_name, False)

            bit_rate = get_bit_rate()

            is_saved = False
            for i,j in zip(dir_list, tracks):
                if not is_saved:
                    is_saved = get_album_image(tmp, j.cover)
                success = modify_metadata_ffmpeg(tmp, i, j, bit_rate, is_saved, debug)

                if not success:
                    print("conversion failed...")
                    break
        
        if success:
            remove_wavs(tmp)

        return success
    
    except Exception as e:
        print("something went wrong...")
        print(e)
        return False

if __name__ == "__main__":
    # query:str = "daydream+nation+sonic+youth"

    # print("testing with", query.replace("+", " "))

    # tracks:list[Song] = get_album_from_spotify(query, True)
    # print(tracks)

    # for t in tracks:
    #     print(t)

    save_album_metadata(True)