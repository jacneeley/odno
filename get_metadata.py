import datetime, os, requests, subprocess

from auth import auth_user
from song import Song

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

def convert_date_str(date_time:str):
    '''
        helper function to return date string as a datetime.

        parameters:
            * date_time -> str date to convert to datetime.
    '''

    return datetime.datetime.strptime(date_time, "%Y-%m-%d")

def sort_tracks(track_list:list[str]) -> None:
    n = len(track_list)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            curr = int(track_list[j].split(".")[0].replace("track",""))
            next = int(track_list[j + 1].split(".")[0].replace("track",""))
            if curr > next:
                track_list[j], track_list[j + 1] = track_list[j + 1] , track_list[j]
                swapped = True
        if not swapped:
            break

def get_album_from_spotify(album_name:str, debug:bool) -> list[Song]:
    '''
        search for an album using the spotify api and get the metadata for each track.

        returns a list of Songs -> list[Song]

        parameters:
            * album_name: name of the album used to search for.
    '''

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

def get_bit_rate() -> int:
    print("Select an mp3 bit rate:")
    print("Smaller bit rate = less fidelity but smaller file size.\n192kb is recommended")
    print("1. 64\n2. `128\n,3. 192\n,4. 256\n5. 320")
    
    selection = int(input("make a selection:"))
    if selection == 1:
        return 64
    elif selection == 2:
        return 128
    elif selection == 3:
        return 192
    elif selection == 4:
        return 256
    elif selection == 5:
        return 320
    else:
        print("invalid selection.\nTry again.")
        return get_bit_rate()

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
    ffmpeg_cmd = ""
    title = f'{"".join(e for e in song.title if e.isalnum())}.wav'
    cp_cmd = f'cp {path.split("album")[0]}{file} {path}/{title}'

    if is_saved:
        mp3_title = f'{title.split(".")[0]}.mp3'
        convert = f'ffmpeg -i {path}/{title} -codec:a libmp3lame -b:a {bit_rate}k {path}/{mp3_title}'
        ffmpeg_cmd = f'ffmpeg -i {path}/{mp3_title} -i {path}/cover.jpg -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1 -metadata title="{song.title}" -metadata artist="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata year="{song.year}" -metadata tracknumber="{song.track_num}" -metadata:s:v title="{song.title} album cover" -metadata:s:v comment="{song.title} cover (front)" -disposition:v:1 attached_pic "{mp3_title}" -hide_banner'.strip()

        print(convert)
    else:
        #TODO: write a different command if there is no album image
        ffmpeg_cmd = f'ffmpeg -i {path}/{file} -i -map 0:a -map 1:v -c:a libmp3lame -b:a {bit_rate}k -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1 -metadata title="{song.title}" -metadata artist="{song.album}" -metadata album_artist="{song.album_artist}" -metadata disc="{song.cd}" -metadata year="{song.year}" -metadata tracknumber="{song.track_num}"'.strip()

    if debug:
        print(song)
        print("running:")
        print(cp_cmd, "\n")
        print(convert, "\n")
        print(ffmpeg_cmd, "\n")

    try:
        subprocess.call(cp_cmd, shell=True)
        subprocess.call(convert, shell=True)
        subprocess.call(ffmpeg_cmd, shell=True)
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
            
            tmp = os.path.join(path,"album")
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
                    break
            
        return success
    
    except Exception as e:
        print("something went wrong...")
        print(e)
        return False

if __name__ == "__main__":
    query:str = "daydream+nation+sonic+youth"

    print("testing with", query.replace("+", " "))

    # tracks:list[Song] = get_album_from_spotify(query, True)
    # print(tracks)

    # for t in tracks:
    #     print(t)

    save_album_metadata(True)